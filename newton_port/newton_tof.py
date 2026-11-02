"""มองด้วย ToF บน Newton: เป็ดลาดตระเวนในอพาร์ตเมนต์โดยไม่รู้ตำแหน่งตัวเอง — เห็นแค่ภาพระยะ 8×8 จาก ToF บนหัว

ToF = VL53L5CX แบบที่ติดบนเป็ดจริง (ตำแหน่ง/ทิศจาก site `tof` ใน MJCF, 8×8 โซน, มุม 45°, ไกลสุด 4 ม., 15 Hz,
noise σ = 3 mm + 2 cm·d/4 m แบบ src/mjlab_microduck/sim/tof.py ของ Pollen) — ยิงรังสีด้วย newton.sensors.SensorTiledCamera
ซึ่งเรนเดอร์ depth ทุก world พร้อมกันบน GPU

ตัวคุม (เลือกต่อกลุ่มเลน):
  blind      เดินตรง เลี้ยวสุ่มทุก 4–8 s (ไม่ใช้เซนเซอร์)
  tof        ข้างหน้าใกล้กว่า STOP → หยุดแล้วหมุนไปฝั่งที่โล่งกว่า
  tof_cliff  เหมือน tof + แถวล่างที่ควรเห็นพื้นกลับไกลเกิน (หลุม/บันไดลง) → ถอยหัวหนี
คะแนน (ใช้ตำแหน่งจริงเฉพาะตอนให้คะแนน ตัวคุมไม่เห็น): ห้องที่ไปถึง, ระยะทาง, จำนวนครั้งที่ชน/ติด, ล้ม (รวมตกช่องบันได)

รันจาก ~/IsaacLab:
  .venv/bin/python ~/repos/microduck_rl/newton_port/newton_tof.py --ctl blind,tof,tof_cliff --per 8 --secs 180
  .venv/bin/python ~/repos/microduck_rl/newton_port/newton_tof.py --probe            # พิมพ์ภาพ ToF 8×8 ตอนยืนหน้ากำแพง
"""
import argparse, os, json, math, time
import numpy as np, torch, warp as wp, newton, mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.expanduser("~/repos/microduck_rl/src/mjlab_microduck/robot/microduck/")
ap = argparse.ArgumentParser()
ap.add_argument("--ctl", default="blind,tof,tof_cliff")
ap.add_argument("--policy", default="newton_walk_2000")
ap.add_argument("--per", type=int, default=8)
ap.add_argument("--secs", type=float, default=180)
ap.add_argument("--lane", type=float, default=7.0)
ap.add_argument("--noise", type=float, default=0.03)
ap.add_argument("--pd-kd", dest="pd_kd", type=float, default=0.053)
ap.add_argument("--vx", type=float, default=0.3)
ap.add_argument("--stop", type=float, default=0.35)          # ม. — ข้างหน้าใกล้กว่านี้ = หลบ
ap.add_argument("--spawn", default="living")                 # living | corridor (หันเข้าหาช่องบันได)
ap.add_argument("--probe", action="store_true")
ap.add_argument("--video", default=None); ap.add_argument("--video-every", type=int, default=5)
ap.add_argument("--cam", default="follow:0"); ap.add_argument("--res", default="1280x720")
ap.add_argument("--out", default=None)
a = ap.parse_args()
dev = "cuda:0"
CTL = a.ctl.split(",")
N = 1 if a.probe else len(CTL) * a.per
SPAWNS = {"living": ((-2.0, -1.9), 0.0), "corridor": ((-0.2, 0.6), -math.pi / 2), "wall": ((-3.2, 1.9), math.pi)}   # wall: หันหน้าเข้ากำแพงตะวันตก ห่าง 0.8 ม.
(sx, sy), syaw = SPAWNS["wall" if a.probe else a.spawn]
ROOMS = {"kitchen": (-4, -1, 0.5, 3), "living": (-4, -1, -3, 0.5), "corridor": (-1, 0.5, -3, 3), "bedroom": (0.5, 4, 1, 3), "office": (0.5, 4, -1, 1), "bath": (0.5, 4, -3, -1)}

# ---------------------------------------------------------------- policy
P = np.load(os.path.join(HERE, a.policy + ".npz")); T = lambda k: torch.tensor(P[k], device=dev)
mean, std, layers, default = T("mean")[0], T("std")[0], [(T(f"w{k}"), T(f"b{k}")) for k in range(4)], T("default_pose")
def policy(obs):
    x = (obs - mean) / std
    for k, (w, b) in enumerate(layers):
        x = x @ w.T + b
        if k < 3: x = torch.nn.functional.elu(x)
    return x

# ---------------------------------------------------------------- ฉาก (เหมือน newton_delivery.py)
mj = mujoco.MjModel.from_xml_path(f"{ROBOT}scene_apartment.xml")
def xf(pos, quat=(1, 0, 0, 0)): return wp.transform(wp.vec3(*map(float, pos)), wp.quat(float(quat[1]), float(quat[2]), float(quat[3]), float(quat[0])))
FLOOR = {"kitchen": (0.74, 0.79, 0.71), "living": (0.62, 0.48, 0.28), "cor": (0.45, 0.42, 0.40), "bedroom": (0.61, 0.53, 0.72), "office": (0.73, 0.48, 0.39), "bath": (0.71, 0.82, 0.88)}
def color(name, g):
    if name.startswith("floor_") and mj.geom_contype[g] == 0:
        key = name[6:].rsplit("_", 1)[0] if name[6:] not in FLOOR else name[6:]
        if key in FLOOR: return wp.vec3(*FLOOR[key])
    if name in ("floor_w", "floor_e") or name.startswith("floor_corridor"): return wp.vec3(0.40, 0.40, 0.42)
    if name.startswith(("wall_", "wA", "wB", "wC", "wF", "wG")): return wp.vec3(0.86, 0.85, 0.82)
    m = mj.geom_matid[g]; c = mj.mat_rgba[m] if m >= 0 else mj.geom_rgba[g]; return wp.vec3(*map(float, c[:3]))
def apartment(b):
    for g in range(mj.ngeom):
        if mj.geom_bodyid[g] != 0: continue
        name = mujoco.mj_id2name(mj, mujoco.mjtObj.mjOBJ_GEOM, g) or ""; typ, s = mj.geom_type[g], mj.geom_size[g]
        cfg = newton.ModelBuilder.ShapeConfig(mu=1.0); pos = mj.geom_pos[g].copy()
        if mj.geom_contype[g] == 0 and mj.geom_conaffinity[g] == 0:
            cfg.has_shape_collision = False
            if name.startswith(("floor_", "rug_")): pos[2] += 0.0045
        kw = dict(xform=xf(pos, mj.geom_quat[g]), cfg=cfg, color=color(name, g), label=name)
        if typ == mujoco.mjtGeom.mjGEOM_BOX: b.add_shape_box(-1, hx=float(s[0]), hy=float(s[1]), hz=float(s[2]), **kw)
        elif typ == mujoco.mjtGeom.mjGEOM_CYLINDER: b.add_shape_cylinder(-1, radius=float(s[0]), half_height=float(s[1]), **kw)
        elif typ == mujoco.mjtGeom.mjGEOM_SPHERE: b.add_shape_sphere(-1, radius=float(s[0]), **kw)

scene = newton.ModelBuilder()
for i in range(N):
    duck = newton.ModelBuilder()
    duck.add_mjcf(f"{ROBOT}robot_groundcontact.xml", floating=True, parse_visuals=True, enable_self_collisions=False)
    nd_duck, nq_duck = duck.joint_dof_count, duck.joint_coord_count
    for j in range(6, nd_duck):
        duck.joint_effort_limit[j] = 0.96; duck.joint_target_kd[j] = a.pd_kd
    yaw0 = syaw + (0 if a.probe else (i % a.per) * 2 * math.pi / a.per)            # แต่ละเลนเริ่มหันคนละทิศ
    duck.joint_q[0:7] = [sx, sy, 0.13, 0, 0, math.sin(yaw0 / 2), math.cos(yaw0 / 2)]
    duck.joint_q[7:nq_duck] = default.cpu().tolist()
    TQ = slice(7, nq_duck) if len(duck.joint_target_q) == duck.joint_coord_count else slice(6, nd_duck)
    duck.joint_target_q[TQ] = default.cpu().tolist()
    HEAD = [k for k, l in enumerate(duck.body_label) if l.endswith("jaw_soft")][0]
    apartment(duck)
    scene.add_world(duck, xform=wp.transform(wp.vec3(0.0, a.lane * i, 0.0), wp.quat_identity()))
model = scene.finalize(device=dev)
ND, NQ, NB = model.joint_dof_count // N, model.joint_coord_count // N, model.body_count // N
solver = newton.solvers.SolverMuJoCo(model, iterations=10, ls_iterations=50, integrator="euler", nconmax=200, njmax=800)
s0, s1, ctrl = model.state(), model.state(), model.control()
newton.eval_fk(model, model.joint_q, model.joint_qd, s0)
Q = lambda st: wp.to_torch(st.joint_q).view(N, NQ); QD = lambda st: wp.to_torch(st.joint_qd).view(N, ND)
torch.manual_seed(0)
Q(s0)[:, 7:nq_duck] += (torch.rand(N, 14, device=dev) * 2 - 1) * a.noise
newton.eval_fk(model, s0.joint_q, s0.joint_qd, s0)
tgt = wp.to_torch(ctrl.joint_target_q).view(N, -1); tgt[:, TQ] = default
trunk = torch.arange(N, device=dev) * NB; head = trunk + HEAD
origin = wp.to_torch(s0.body_q)[trunk][:, :2].clone() - torch.tensor([sx, sy], device=dev)
SUB, dt = 4, 0.005

# ---------------------------------------------------------------- ToF: site `tof` บน jaw_soft → กล้อง pinhole 8×8 (กล้องมองทาง −z, site มองทาง +x)
def qmul(a_, b_):                                   # xyzw
    ax, ay, az, aw = a_.unbind(-1); bx, by, bz, bw = b_.unbind(-1)
    return torch.stack([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz], -1)
def qrot(q, v):
    x, y, z, w = q.unbind(-1); u = torch.stack([x, y, z], -1); t = 2 * torch.cross(u, v, dim=-1)
    return v + w.unsqueeze(-1) * t + torch.cross(u, t, dim=-1)
sid = mujoco.mj_name2id(mj, mujoco.mjtObj.mjOBJ_SITE, "tof")
SITE_P = torch.tensor(mj.site_pos[sid], device=dev, dtype=torch.float32)
w_, x_, y_, z_ = mj.site_quat[sid]; SITE_Q = torch.tensor([x_, y_, z_, w_], device=dev, dtype=torch.float32)
CAM_Q = torch.tensor([0.5, -0.5, -0.5, 0.5], device=dev)       # กล้อง (−z หน้า, +y บน) → site (+x หน้า, +z บน)
TOF_W = 8; FOV = math.radians(45.0); MAXR = 4.0
cam_sensor = newton.sensors.SensorTiledCamera(model)
rays = cam_sensor.utils.compute_camera_rays_pinhole(TOF_W, TOF_W, camera_fovs=FOV)
depth = cam_sensor.utils.create_depth_image_output(TOF_W, TOF_W)
cam_tf = wp.zeros((1, N), dtype=wp.transformf, device=dev)
gen = torch.Generator(device=dev).manual_seed(1)
def tof_frame():
    bq = wp.to_torch(s0.body_q)[head]
    pos = bq[:, :3] + qrot(bq[:, 3:7], SITE_P.expand(N, 3)); q = qmul(qmul(bq[:, 3:7], SITE_Q.expand(N, 4)), CAM_Q.expand(N, 4))
    wp.to_torch(cam_tf).view(1, N, 7).copy_(torch.cat([pos, q], 1).unsqueeze(0))
    model.bvh_refit_shapes(s0) if hasattr(model, "bvh_refit_shapes") else None
    cam_sensor.update(s0, cam_tf, rays, depth_image=depth)
    d = wp.to_torch(depth).view(N, TOF_W, TOF_W).clone()                   # แถว 0 = บนสุด
    nohit = (d < 0) | (d > MAXR)
    d = d + torch.randn(d.shape, device=dev, generator=gen) * (0.003 + 0.02 * d.clamp(min=0) / MAXR)
    return torch.where(nohit, torch.full_like(d, float("inf")), d.clamp(min=0))

# ---------------------------------------------------------------- loop พื้นฐาน
def quat_rot_inv(qxyzw, v):
    x, y, z, w = qxyzw.unbind(-1); u = torch.stack([-x, -y, -z], -1); t = 2 * torch.cross(u, v, dim=-1)
    return v + w.unsqueeze(-1) * t + torch.cross(u, t, dim=-1)
bqd_lag = wp.zeros_like(s0.body_qd); bq_lag = wp.zeros_like(s0.body_q)
def physics():
    global s0, s1
    for i in range(SUB):
        if i == SUB - 1: wp.copy(bqd_lag, s0.body_qd); wp.copy(bq_lag, s0.body_q)
        s0.clear_forces(); solver.step(s0, s1, ctrl, None, dt); s0, s1 = s1, s0
q0 = Q(s0).clone(); physics()
with wp.ScopedCapture() as cap: physics()
graph = cap.graph
Q(s0).copy_(q0); QD(s0).zero_(); newton.eval_fk(model, s0.joint_q, s0.joint_qd, s0)
cmd = torch.zeros(N, 13, device=dev); last = torch.zeros(N, 14, device=dev)
def obs_now(k):
    bq = wp.to_torch(s0.body_q)[trunk]
    src_q, src_qd = (bq_lag, bqd_lag) if k > 0 else (s0.body_q, s0.body_qd)
    quat = wp.to_torch(src_q)[trunk][:, 3:7]; w = wp.to_torch(src_qd)[trunk][:, 3:6]
    grav = quat_rot_inv(quat, torch.tensor([0., 0., -1.], device=dev).expand(N, 3))
    return torch.cat([quat_rot_inv(quat, w), grav, Q(s0)[:, 7:nq_duck] - default, QD(s0)[:, 6:nd_duck], last, cmd], 1), bq

if a.probe:                                          # ยืนนิ่ง 1 s แล้วพิมพ์ภาพ ToF
    with torch.no_grad():
        for k in range(50):
            obs, bq = obs_now(k); act = policy(obs); last = act; tgt[:, TQ] = default + act; wp.capture_launch(graph)
    D = tof_frame()[0].cpu().numpy()
    bq = wp.to_torch(s0.body_q)[head][0].cpu().numpy()
    print("head z %.3f · trunk at (%.2f, %.2f) yaw %.0f° · wall x = -4.0 (inner face -3.94)" % (bq[2], sx, sy, math.degrees(syaw)))
    for r in range(TOF_W): print(" ".join("  inf" if not np.isfinite(v) else f"{v:5.2f}" for v in D[r]))
    raise SystemExit

# ---------------------------------------------------------------- ตัวคุม (เห็นแค่ ToF + gyro, ไม่เห็นตำแหน่ง)
cid = torch.tensor([CTL.index(CTL[i // a.per]) for i in range(N)], device=dev)
K_TOF, K_TOFC = CTL.index("tof") if "tof" in CTL else -1, CTL.index("tof_cliff") if "tof_cliff" in CTL else -1
mode = torch.zeros(N, dtype=torch.long, device=dev)            # 0 เดิน · 1 หมุนหลบ
turn_dir = torch.ones(N, device=dev); turn_until = torch.zeros(N, device=dev); next_rand = torch.rand(N, device=dev, generator=gen) * 4 + 4
ROW7 = math.atan((7.5 / 8 - 0.5) * 2 * math.tan(FOV / 2))     # มุมก้มของแถวล่างสุด (≈ 19.9°)
def control(t, D):
    centre = D[:, 2:6, 2:6].flatten(1)
    front = centre.min(1).values                               # สิ่งกีดขวางข้างหน้าที่ใกล้สุด (แถว/คอลัมน์กลาง)
    left, right = D[:, 1:6, :3].mean((1, 2)), D[:, 1:6, 5:].mean((1, 2))
    # พื้นที่ควรเห็น: แถวล่างสุดยิงต่ำกว่าแนวราบ ~20° → ระยะถึงพื้น ≈ ความสูงหัว / sin(20°) (≈ 0.66 ม. ตอนยืน)
    hz = wp.to_torch(s0.body_q)[head][:, 2]
    floor_exp = hz / math.sin(ROW7)
    floor_now = D[:, 7, 2:6].median(1).values
    cliff = floor_now > floor_exp * 1.35 + 0.05                # พื้นข้างหน้าไกลกว่าที่ควร (หรือไม่เจอเลย) = หลุม/บันไดลง
    blocked = front < a.stop
    walking = mode == 0
    use_tof = (cid == K_TOF) | (cid == K_TOFC)
    start_turn = walking & use_tof & (blocked | ((cid == K_TOFC) & cliff))
    # blind: เลี้ยวสุ่ม 1–2 s ทุก 4–8 s
    rnd = walking & (cid != K_TOF) & (cid != K_TOFC) & (t > next_rand)
    nd = torch.where(left > right, 1.0, -1.0)
    turn_dir[start_turn] = nd[start_turn]; turn_dir[rnd] = torch.where(torch.rand(N, device=dev, generator=gen) > 0.5, 1.0, -1.0)[rnd]
    dur = torch.where(start_turn, 0.8 + torch.rand(N, device=dev, generator=gen) * 1.2, 1.0 + torch.rand(N, device=dev, generator=gen))
    turn_until[start_turn | rnd] = t + dur[start_turn | rnd]; mode[start_turn | rnd] = 1
    next_rand[rnd] = t + 4 + torch.rand(N, device=dev, generator=gen)[rnd] * 4
    fin = (mode == 1) & (t > turn_until) & ~(use_tof & blocked)   # หมุนจนข้างหน้าโล่ง
    mode[fin] = 0
    cmd[:, 0] = torch.where(mode == 0, a.vx, 0.0); cmd[:, 2] = torch.where(mode == 1, 0.8 * turn_dir, 0.0)
    return front, cliff

# ---------------------------------------------------------------- คะแนน (ตำแหน่งจริง ใช้แค่ให้คะแนน)
visited = torch.zeros(N, len(ROOMS), dtype=torch.bool, device=dev)
RB = torch.tensor(list(ROOMS.values()), device=dev)
fell = torch.zeros(N, dtype=torch.bool, device=dev); t_fall = torch.full((N,), float("nan"), device=dev); fall_xy = torch.full((N, 2), float("nan"), device=dev)
tilt_t = torch.full((N,), -1.0, device=dev); stuck = torch.zeros(N, dtype=torch.long, device=dev); dist = torch.zeros(N, device=dev)
prev_p = None; stuck_since = torch.full((N,), -1.0, device=dev); n_turns = torch.zeros(N, dtype=torch.long, device=dev); cliff_seen = torch.zeros(N, dtype=torch.long, device=dev)
def score(t, bq):
    global prev_p
    p = bq[:, :2] - origin; x, y = bq[:, 3], bq[:, 4]
    alive = ~fell
    inside = (p[:, None, 0] >= RB[:, 0]) & (p[:, None, 0] < RB[:, 1]) & (p[:, None, 1] >= RB[:, 2]) & (p[:, None, 1] < RB[:, 3])
    visited[:] = visited | (inside & alive[:, None])
    if prev_p is None or round(t / 0.02) % 25 == 0:
        if prev_p is not None:
            step = (p - prev_p).norm(dim=1); dist[alive] += step[alive]
            jam = alive & (cmd[:, 0] > 0.1) & (step < 0.02)            # สั่งเดินแต่ไม่ขยับใน 0.5 s = ชน/ติด
            stuck[jam & (stuck_since < 0)] += 1; stuck_since[jam & (stuck_since < 0)] = t; stuck_since[~jam] = -1
        prev_p = p.clone()
    up = 1 - 2 * (x * x + y * y); tilted = alive & ((up < 0.55) | (bq[:, 2] < 0.04))
    tilt_t[tilted & (tilt_t < 0)] = t; tilt_t[~tilted] = -1
    f = tilted & (t - tilt_t > 0.5); fell[f] = True; t_fall[f] = t; fall_xy[f] = p[f]

# ---------------------------------------------------------------- viewer
viewer = None
if a.video:
    import newton.viewer
    from PIL import Image
    W, H = map(int, a.res.split("x"))
    viewer = newton.viewer.ViewerGL(width=W, height=H, headless=True); viewer.set_model(model); viewer.set_world_offsets((0.0, 0.0, 0.0))
    os.makedirs(a.video, exist_ok=True)
    def cam(bq):
        kind, _, arg = a.cam.partition(":"); i = int(arg)
        if kind == "top":
            viewer.set_camera(wp.vec3(0.0, float(origin[i, 1]) - 3.4, 8.2), -66.0, 90.0)
        else:
            fx, fy, fz = (float(v) for v in bq[i, :3]); viewer.set_camera(wp.vec3(fx - 0.5, fy - 0.7, fz + 0.75), -42.0, 55.0)
    tof_log = []

steps = int(a.secs * 50); torch.cuda.synchronize(); t0 = time.time(); nf = 0; D = None
with torch.no_grad():
    for k in range(steps):
        t = k * 0.02
        obs, bq = obs_now(k); score(t, bq)
        if k % 3 == 0 and k >= 50:                       # ToF 16.7 Hz (ตัวจริง 15 Hz) — เริ่มหลังยืนนิ่ง 1 s
            D = tof_frame(); front, cliff = control(t, D)
            cliff_seen += (cliff & ~fell).long()
        if k < 50: cmd[:, 0] = 0; cmd[:, 2] = 0
        cmd[fell] = 0
        obs[:, -13:] = cmd
        act = policy(obs); last = act; tgt[:, TQ] = default + act
        wp.capture_launch(graph)
        if viewer is not None and k % a.video_every == 0:
            cam(wp.to_torch(s0.body_q)[trunk]); viewer.begin_frame(t); viewer.log_state(s0); viewer.end_frame()
            Image.fromarray(viewer.get_frame().numpy()).save(f"{a.video}/f_{nf:04d}.png"); nf += 1
            ci = int(a.cam.partition(":")[2])
            tof_log.append(None if D is None else D[ci].cpu().numpy().tolist())
torch.cuda.synchronize(); wall = time.time() - t0

res = dict(N=N, sim_s=round(t, 1), wall_s=round(wall, 1), spawn=a.spawn, policy=a.policy, stop=a.stop, lanes=[], groups={})
names = list(ROOMS)
for i in range(N):
    res["lanes"].append(dict(ctl=CTL[i // a.per], rooms=[names[j] for j in range(len(names)) if visited[i, j]], n_rooms=int(visited[i].sum()), dist_m=round(float(dist[i]), 2),
                             stuck=int(stuck[i]), fell=bool(fell[i]), t_fall=None if math.isnan(float(t_fall[i])) else round(float(t_fall[i]), 1),
                             fall_xy=None if math.isnan(float(fall_xy[i, 0])) else [round(float(v), 2) for v in fall_xy[i]]))
for c in CTL:
    L = [l for l in res["lanes"] if l["ctl"] == c]
    res["groups"][c] = dict(n=len(L), rooms_mean=round(sum(l["n_rooms"] for l in L) / len(L), 2), dist_mean=round(sum(l["dist_m"] for l in L) / len(L), 2),
                            stuck_mean=round(sum(l["stuck"] for l in L) / len(L), 2), fell=sum(l["fell"] for l in L))
print(json.dumps({k: v for k, v in res.items() if k != "lanes"}, ensure_ascii=False))
if a.out: json.dump(res, open(a.out, "w"), ensure_ascii=False, indent=1)
if a.video: json.dump(tof_log, open(os.path.join(a.video, "tof.json"), "w"))
