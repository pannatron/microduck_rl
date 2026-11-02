"""Microduck บน Newton: รัน policy (npz จาก onnx2npz.py) กับเป็ด N ตัวพร้อมกันบน GPU แล้ววัดความเร็วเทียบคำสั่ง

รันจาก ~/IsaacLab (venv ที่มี newton):
  .venv/bin/python ~/repos/microduck_rl/newton_port/newton_duck.py --policy walk_2000 --solver mujoco --cmds 0.2,0.25,0.3,0.4 --per-cmd 16

แต่ละเป็ดอยู่ใน "world" ของตัวเอง (ชนกันไม่ได้) — คำสั่งต่างกันได้ทีละตัว
obs 61 มิติ = gyro 3 + projected gravity 3 + joint pos−default 14 + joint vel 14 + last action 14 + command 13
(ลำดับเดียวกับ scripts/infer_policy.py)
"""
import argparse, os, time, json
import numpy as np, torch, warp as wp, newton

HERE = os.path.dirname(os.path.abspath(__file__))
XML = os.path.expanduser("~/repos/microduck_rl/src/mjlab_microduck/robot/microduck/robot_groundcontact.xml")
ap = argparse.ArgumentParser()
ap.add_argument("--policy", default="walk_2000")
ap.add_argument("--solver", default="mujoco", choices=["mujoco", "featherstone", "xpbd", "semi"])
ap.add_argument("--cmds", default="0.2,0.25,0.3,0.4")      # vx ที่จะสั่ง (เป็ดแต่ละกลุ่ม)
ap.add_argument("--per-cmd", type=int, default=16)
ap.add_argument("--secs", type=float, default=20.0)
ap.add_argument("--substeps", type=int, default=4)          # sim dt = 0.02 / substeps (ค่าเดิม 0.005)
ap.add_argument("--effort", type=float, default=0.96)       # forcerange ของ position actuator ใน MJCF
ap.add_argument("--out", default=None)
ap.add_argument("--graph", type=int, default=1)
ap.add_argument("--integrator", default="euler")          # euler | implicitfast | rk4 (MJCF ของเป็ดไม่ได้ระบุ = euler ใน MuJoCo)
ap.add_argument("--noise", type=float, default=0.03)    # สุ่มมุมข้อต่อเริ่มต้น ±rad ให้เป็ดแต่ละตัวไม่เหมือนกันเป๊ะ
ap.add_argument("--iters", type=int, default=10)        # solver iterations (mjlab ตอนเทรน = 10, MuJoCo CPU ค่าปกติ = 100)
ap.add_argument("--video", default=None)                 # บันทึกวิดีโอจาก Newton ViewerGL (headless) เป็นโฟลเดอร์ภาพ PNG
ap.add_argument("--video-every", type=int, default=2)   # เก็บทุก N control step (50 Hz / N fps)
ap.add_argument("--cam", default="2.5,-2.5,1.6,-25,135")  # x,y,z,pitch,yaw
ap.add_argument("--res", default="1280x720")
ap.add_argument("--follow", type=int, default=-1)        # >=0: กล้องตามเป็ดตัวที่ระบุ (dx,dy,dz จาก --cam ใช้เป็น offset)
ap.add_argument("--spacing", type=float, default=1.0)
ap.add_argument("--pd-kd", dest="pd_kd", type=float, default=0.0)   # D-gain ของ PD (Isaac Lab DelayedPD ใช้ 0.053; MJCF position actuator = 0)
ap.add_argument("--head-rand", type=int, default=0)     # 1 = สุ่มเป้าหัว (pitch ±0.4, yaw ±0.8 rad) ทุก 3 s แล้ววัด error
ap.add_argument("--act-delay", type=int, default=0)     # คำสั่งมอเตอร์ช้า N physics substep (5 ms ต่อ substep) — Pollen เทรน 3–6
ap.add_argument("--jv-lag", type=int, default=0)        # joint vel ใน obs ช้า 1 control step (แบบ Dynamixel)
ap.add_argument("--sensor-lag", type=int, default=1)    # 1 = gyro ช้าไป 1 substep เหมือน sensor ของ mj_step (ค่าที่ policy เห็นตอนเทรน)
ap.add_argument("--selfcol", type=int, default=0)       # self-collision ระหว่างชิ้นส่วนเป็ด (Newton ตั้ง True เป็นค่าเริ่มต้น)
ap.add_argument("--dump", default=None)                  # บันทึก obs/action 50 step แรกของเป็ดตัวแรก
ap.add_argument("--cpu", type=int, default=0)          # SolverMuJoCo(use_mujoco_cpu=True)
ap.add_argument("--save-mjcf", default=None)
ap.add_argument("--kd", type=float, default=None)   # contact damping สำหรับ solver ที่ไม่ใช่ MuJoCo (ค่า default ของ Newton = 100)
ap.add_argument("--ke", type=float, default=None)
ap.add_argument("--film", default=None)                     # บันทึก trajectory ไว้วาด/เรนเดอร์ภายหลัง
a = ap.parse_args()
dev = "cuda:0"

# ---------------------------------------------------------------- policy (MLP ใน torch)
P = np.load(os.path.join(HERE, a.policy + ".npz"))
T = lambda k: torch.tensor(P[k], device=dev)
mean, std = T("mean")[0], T("std")[0]
layers = [(T(f"w{k}"), T(f"b{k}")) for k in range(4)]
default = T("default_pose")
def policy(obs):
    x = (obs - mean) / std
    for k, (w, b) in enumerate(layers):
        x = x @ w.T + b
        if k < 3: x = torch.nn.functional.elu(x)
    return x

# ---------------------------------------------------------------- scene
cmds = [float(c) for c in a.cmds.split(",")]
N = len(cmds) * a.per_cmd
duck = newton.ModelBuilder()
duck.add_mjcf(XML, floating=True, parse_visuals=bool(a.video), enable_self_collisions=bool(a.selfcol))
nd = duck.joint_dof_count; nq = duck.joint_coord_count            # 20, 21
for i in range(6, nd):
    duck.joint_effort_limit[i] = a.effort
    duck.joint_target_kd[i] = a.pd_kd
duck.joint_q[0:7] = [0, 0, 0.125, 0, 0, 0, 1]                      # xyz + quat (x,y,z,w)
duck.joint_q[7:] = P["default_pose"].tolist()
duck.joint_target_q[-14:] = P["default_pose"].tolist()          # ช่องท้าย 14 ช่อง = ข้อต่อ (ใช้ได้ทั้ง layout แบบ DOF และ coord)
if a.kd is not None or a.ke is not None:
    for i in range(duck.shape_count):
        if a.kd is not None: duck.shape_material_kd[i] = a.kd
        if a.ke is not None: duck.shape_material_ke[i] = a.ke
scene = newton.ModelBuilder()
scene.replicate(duck, N, spacing=(a.spacing, a.spacing, 0.0))
scene.add_ground_plane()
model = scene.finalize(device=dev)

if a.solver == "mujoco":
    solver = newton.solvers.SolverMuJoCo(model, iterations=a.iters, ls_iterations=50, integrator=a.integrator, nconmax=64, njmax=256,
                                          use_mujoco_cpu=bool(a.cpu), save_to_mjcf=a.save_mjcf)            # ต่อ world
    contacts = None
elif a.solver == "featherstone":
    solver = newton.solvers.SolverFeatherstone(model)
elif a.solver == "xpbd":
    solver = newton.solvers.SolverXPBD(model, iterations=8)
else:
    solver = newton.solvers.SolverSemiImplicit(model)
s0, s1, ctrl = model.state(), model.state(), model.control()
newton.eval_fk(model, model.joint_q, model.joint_qd, s0)

q = wp.to_torch(s0.joint_q).view(N, nq)
torch.manual_seed(0)
q[:, 7:] += (torch.rand(N, 14, device=dev) * 2 - 1) * a.noise
newton.eval_fk(model, s0.joint_q, s0.joint_qd, s0)
tgt = wp.to_torch(ctrl.joint_target_q).view(N, -1)
tgt[:, -14:] = default
dt = 0.02 / a.substeps

cmd = torch.zeros(N, 13, device=dev)
cmd[:, 0] = torch.tensor(cmds, device=dev).repeat_interleave(a.per_cmd)
last = torch.zeros(N, 14, device=dev)
trunk = torch.arange(N, device=dev) * duck.body_count               # body index ของ trunk_base ในแต่ละ world

def quat_rot_inv(qxyzw, v):                                         # หมุนเวกเตอร์ world → body
    x, y, z, w = qxyzw.unbind(-1); u = torch.stack([-x, -y, -z], -1)
    t = 2 * torch.cross(u, v, dim=-1)
    return v + w.unsqueeze(-1) * t + torch.cross(u, t, dim=-1)

def obs_now(st):
    bq = wp.to_torch(st.body_q)[trunk]
    lag = a.sensor_lag and k_step[0] > 0
    bqd = wp.to_torch(bqd_lag if lag else st.body_qd)[trunk]
    quat = (wp.to_torch(bq_lag)[trunk] if lag else bq)[:, 3:7]          # xquat ของ MuJoCo ก็ช้า 1 substep เหมือนกัน
    gyro = quat_rot_inv(quat, bqd[:, 3:6])                          # body_qd = [v_lin, w] ใน world frame
    grav = quat_rot_inv(quat, torch.tensor([0., 0., -1.], device=dev).expand(N, 3))
    jq = wp.to_torch(st.joint_q).view(N, nq)[:, 7:]; jqd = wp.to_torch(st.joint_qd).view(N, nd)[:, 6:].clone()
    if a.jv_lag:
        jqd, jv_prev[0] = (jv_prev[0] if jv_prev[0] is not None else jqd), jqd
    return torch.cat([gyro, grav, jq - default, jqd, last, cmd], 1), bq

def yaw_of(bq):
    x, y, z, w = bq[:, 3:7].unbind(-1)
    return torch.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))

steps = int(a.secs * 50)
log_xy, log_yaw, log_z = [], [], []
DUMP = []
head_err = []
k_step = [0]
jv_prev = [None]
# ความหน่วงคำสั่งมอเตอร์: substep i ของ control step k ใช้ target ของ control step (4k+i-d)//4
tgt_sub = [wp.clone(ctrl.joint_target_q) for _ in range(a.substeps)]
tgt_hist = []
bqd_lag = wp.zeros_like(s0.body_qd); bq_lag = wp.zeros_like(s0.body_q)                 # body_qd ก่อน substep สุดท้าย (ไว้ทำ gyro แบบ MuJoCo)
def physics():
    global s0, s1
    for i in range(a.substeps):
        if a.act_delay: wp.copy(ctrl.joint_target_q, tgt_sub[i])
        if i == a.substeps - 1: wp.copy(bqd_lag, s0.body_qd); wp.copy(bq_lag, s0.body_q)
        s0.clear_forces()
        if a.solver == "mujoco":
            solver.step(s0, s1, ctrl, None, dt)
        else:
            solver.step(s0, s1, ctrl, model.collide(s0), dt)
        s0, s1 = s1, s0
    if a.solver in ("semi", "xpbd"):              # solver แบบ maximal coordinates ไม่อัปเดต joint_q เอง
        newton.eval_ik(model, s0, s0.joint_q, s0.joint_qd)
graph = None
q0 = wp.to_torch(s0.joint_q).clone()
if a.graph and a.substeps % 2 == 0:
    physics()                                   # warm-up: คอมไพล์ kernel ก่อน capture
    with wp.ScopedCapture() as cap:
        physics()
    graph = cap.graph
    wp.to_torch(s0.joint_q).copy_(q0); wp.to_torch(s0.joint_qd).zero_()   # เริ่มใหม่จากท่าเริ่มเดิม
    newton.eval_fk(model, s0.joint_q, s0.joint_qd, s0)
viewer = None
if a.video:
    import newton.viewer
    W, H = map(int, a.res.split("x"))
    viewer = newton.viewer.ViewerGL(width=W, height=H, headless=True)
    viewer.set_model(model)
    cx, cy, cz, cp, cyaw = map(float, a.cam.split(","))
    viewer.set_camera(wp.vec3(cx, cy, cz), cp, cyaw)
    os.makedirs(a.video, exist_ok=True)
    from PIL import Image
torch.cuda.synchronize(); t0 = time.time()
with torch.no_grad():
    for k in range(steps):
        k_step[0] = k
        if a.head_rand and k % 150 == 0:          # เปลี่ยนเป้าหัวทุก 3 s
            cmd[:, 4] = (torch.rand(N, device=dev) * 2 - 1) * 0.4
            cmd[:, 5] = (torch.rand(N, device=dev) * 2 - 1) * 0.8
        if a.head_rand:
            hq = wp.to_torch(s0.joint_q).view(N, nq)[:, 7:][:, 5:9] - default[5:9]
            head_err.append((hq - cmd[:, 3:7]).abs().clone())
        obs, bq = obs_now(s0)
        act = policy(obs); last = act
        if a.dump and k < 50: DUMP.append((obs[0].cpu().numpy(), act[0].cpu().numpy()))
        tgt[:, -14:] = default + act
        if a.act_delay:
            tgt_hist.insert(0, tgt.clone()); del tgt_hist[4:]
            for i in range(a.substeps):
                back = k - (a.substeps * k + i - a.act_delay) // a.substeps          # ย้อนไปกี่ control step
                wp.to_torch(tgt_sub[i]).view(N, -1).copy_(tgt_hist[min(back, len(tgt_hist) - 1)])
        if graph is not None: wp.capture_launch(graph)
        else: physics()
        log_xy.append(bq[:, :2].clone()); log_yaw.append(yaw_of(bq)); log_z.append(bq[:, 2].clone())
        if viewer is not None and k % a.video_every == 0:
            if a.follow >= 0:
                fx, fy = bq[a.follow, 0].item(), bq[a.follow, 1].item()
                viewer.set_camera(wp.vec3(fx + cx, fy + cy, cz), cp, cyaw)
            viewer.begin_frame(k * 0.02); viewer.log_state(s0); viewer.end_frame()
            Image.fromarray(viewer.get_frame().numpy()).save(f"{a.video}/f_{k // a.video_every:04d}.png")
torch.cuda.synchronize(); wall = time.time() - t0

XY = torch.stack(log_xy); YAW = torch.stack(log_yaw); Z = torch.stack(log_z)       # [steps, N, ...]
h = steps // 2                                                                      # วัดครึ่งหลัง (10 s สุดท้าย)
d = XY[-1] - XY[h]; secs = (steps - h) / 50
yaw_mid = YAW[h:].mean(0)
dyaw = torch.atan2(torch.sin(YAW[-1] - YAW[h]), torch.cos(YAW[-1] - YAW[h]))
# ความเร็วไปข้างหน้า: ระยะในทิศหัว (เฉลี่ย 1 วินาทีต่อช่วง) กันกรณีเดินโค้ง
seg = 50; fwd = []
for i in range(h, steps - seg, seg):
    dd = XY[i + seg] - XY[i]; yy = YAW[i]
    fwd.append((dd[:, 0] * torch.cos(yy) + dd[:, 1] * torch.sin(yy)) / (seg / 50))
fwd = torch.stack(fwd).mean(0)
fell = (Z.min(0).values < 0.07)
res = {"policy": a.policy, "solver": a.solver, "N": N, "secs": a.secs, "wall_s": round(wall, 2),
       "realtime_x": round(a.secs * N / wall, 1), "rows": []}
for i, c in enumerate(cmds):
    sl = slice(i * a.per_cmd, (i + 1) * a.per_cmd); ok = ~fell[sl]
    res["rows"].append({"cmd": c, "fwd": round(fwd[sl][ok].mean().item(), 3) if ok.any() else None,
                        "fwd_std": round(fwd[sl][ok].std().item(), 3) if ok.sum() > 1 else None,
                        "yaw_rate": round((dyaw[sl][ok] / secs).mean().item(), 3) if ok.any() else None,
                        "fell": int(fell[sl].sum().item()), "n": a.per_cmd})
if a.head_rand:
    E = torch.stack(head_err)[steps // 2:]             # [t, N, 4]
    res["head_mae_deg"] = {"head_pitch": round(float(E[..., 1].mean()) * 57.3, 1), "head_yaw": round(float(E[..., 2].mean()) * 57.3, 1)}
print(json.dumps(res))
if a.out:
    open(a.out, "a").write(json.dumps(res) + "\n")
if a.dump:
    np.savez(a.dump, obs=np.array([d[0] for d in DUMP]), act=np.array([d[1] for d in DUMP]))
if a.film:
    np.savez(a.film, xy=XY.cpu().numpy(), yaw=YAW.cpu().numpy(), z=Z.cpu().numpy(), cmds=np.array(cmds), per=a.per_cmd)
