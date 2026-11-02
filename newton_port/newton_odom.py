"""ไม่มี GPS: เป็ดเดินสี่เหลี่ยม 1.5×1.5 ม. ตาม "ตำแหน่งที่คิดว่าอยู่" (dead reckoning) — แล้ววัดว่าจบห่างจุดเริ่มจริงเท่าไร

ทุกเลนเริ่มที่จุดเดียวกัน (world ซ้อนกัน) จึงเห็นเป็ดกระจายออกเป็นกลุ่มเมฆในภาพ
ตัวประมาณตำแหน่ง (เลือกต่อกลุ่มเลน):
  cmd       ทิศ = ∫ คำสั่งเลี้ยว · ระยะ = ∫ คำสั่งเดิน          (เชื่อว่าเป็ดทำตามคำสั่งเป๊ะ)
  gyro      ทิศ = ∫ gyro z ของ IMU (มี bias สุ่ม ±0.3°/s + noise) · ระยะ = ∫ คำสั่งเดิน
  gyro_cal  เหมือน gyro + คูณระยะด้วย k = ความเร็วจริง/คำสั่ง ที่วัดจากการเดินตรงก่อนหน้า (--calib)
  gyro_still  เหมือน gyro_cal + หา bias ของ gyro ตอนยืนนิ่ง 1 s แรก แล้วลบออก
ตำแหน่งจริงใช้แค่ให้คะแนน

รันจาก ~/IsaacLab:
  .venv/bin/python ~/repos/microduck_rl/newton_port/newton_odom.py --calib                 # หา k
  .venv/bin/python ~/repos/microduck_rl/newton_port/newton_odom.py --est cmd,gyro,gyro_cal --per 32 --k <k>
"""
import argparse, os, json, math, time
import numpy as np, torch, warp as wp, newton

HERE = os.path.dirname(os.path.abspath(__file__))
XML = os.path.expanduser("~/repos/microduck_rl/src/mjlab_microduck/robot/microduck/robot_groundcontact.xml")
ap = argparse.ArgumentParser()
ap.add_argument("--policy", default="newton_walk_2000")
ap.add_argument("--est", default="cmd,gyro,gyro_cal")
ap.add_argument("--per", type=int, default=32)
ap.add_argument("--side", type=float, default=1.5)
ap.add_argument("--loops", type=int, default=1)
ap.add_argument("--vx", type=float, default=0.3)
ap.add_argument("--k", type=float, default=1.0)              # ความเร็วจริง / คำสั่ง (จาก --calib)
ap.add_argument("--gyro-bias", dest="gbias", type=float, default=0.3)   # °/s (สุ่มต่อเป็ด ±)
ap.add_argument("--gyro-noise", dest="gnoise", type=float, default=0.02) # rad/s ต่อ sample
ap.add_argument("--calib", action="store_true")
ap.add_argument("--still", type=float, default=1.0)       # ยืนนิ่งกี่วินาทีก่อนออกเดิน (gyro_still ใช้ช่วงหลังครึ่งหนึ่งหา bias)
ap.add_argument("--secs", type=float, default=90)
ap.add_argument("--pd-kd", dest="pd_kd", type=float, default=0.053)
ap.add_argument("--noise", type=float, default=0.03)
ap.add_argument("--video", default=None); ap.add_argument("--video-every", type=int, default=5); ap.add_argument("--res", default="1280x720")
ap.add_argument("--out", default=None)
a = ap.parse_args()
dev = "cuda:0"
EST = ["calib"] if a.calib else a.est.split(",")
N = len(EST) * a.per

P = np.load(os.path.join(HERE, a.policy + ".npz")); T = lambda k: torch.tensor(P[k], device=dev)
mean, std, layers, default = T("mean")[0], T("std")[0], [(T(f"w{k}"), T(f"b{k}")) for k in range(4)], T("default_pose")
def policy(obs):
    x = (obs - mean) / std
    for k, (w, b) in enumerate(layers):
        x = x @ w.T + b
        if k < 3: x = torch.nn.functional.elu(x)
    return x

duck = newton.ModelBuilder()
duck.add_mjcf(XML, floating=True, parse_visuals=bool(a.video), enable_self_collisions=False)
nd, nq = duck.joint_dof_count, duck.joint_coord_count
for i in range(6, nd):
    duck.joint_effort_limit[i] = 0.96; duck.joint_target_kd[i] = a.pd_kd
duck.joint_q[0:7] = [0, 0, 0.125, 0, 0, 0, 1]; duck.joint_q[7:] = default.cpu().tolist()
TQ = slice(7, nq) if len(duck.joint_target_q) == nq else slice(6, nd)
duck.joint_target_q[TQ] = default.cpu().tolist()
scene = newton.ModelBuilder(); scene.replicate(duck, N, spacing=(0.0, 0.0, 0.0)); scene.add_ground_plane()
if a.video:                                             # เส้นทางที่ตั้งใจ (เส้นเหลือง) + จุดเริ่ม/จุดจบ (วงเขียว) — ไม่ชนอะไร
    vis = newton.ModelBuilder.ShapeConfig(); vis.has_shape_collision = False; S_ = a.side
    for cx, cy, hx, hy in ((S_ / 2, 0, S_ / 2, 0.01), (S_, S_ / 2, 0.01, S_ / 2), (S_ / 2, S_, S_ / 2, 0.01), (0, S_ / 2, 0.01, S_ / 2)):
        scene.add_shape_box(-1, xform=wp.transform(wp.vec3(cx, cy, 0.001), wp.quat_identity()), hx=hx, hy=hy, hz=0.001, cfg=vis, color=wp.vec3(1.0, 0.85, 0.1))
    scene.add_shape_cylinder(-1, xform=wp.transform(wp.vec3(0, 0, 0.002), wp.quat_identity()), radius=0.08, half_height=0.001, cfg=vis, color=wp.vec3(0.2, 0.85, 0.3))
model = scene.finalize(device=dev)
solver = newton.solvers.SolverMuJoCo(model, iterations=10, ls_iterations=50, integrator="euler", nconmax=64, njmax=256)
s0, s1, ctrl = model.state(), model.state(), model.control()
newton.eval_fk(model, model.joint_q, model.joint_qd, s0)
Q = lambda st: wp.to_torch(st.joint_q).view(N, nq); QD = lambda st: wp.to_torch(st.joint_qd).view(N, nd)
torch.manual_seed(0)
Q(s0)[:, 7:] += (torch.rand(N, 14, device=dev) * 2 - 1) * a.noise
newton.eval_fk(model, s0.joint_q, s0.joint_qd, s0)
tgt = wp.to_torch(ctrl.joint_target_q).view(N, -1); tgt[:, TQ] = default
trunk = torch.arange(N, device=dev) * duck.body_count
SUB, dt = 4, 0.005
def qri(q, v):
    x, y, z, w = q.unbind(-1); u = torch.stack([-x, -y, -z], -1); t = 2 * torch.cross(u, v, dim=-1)
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
    gyro = qri(quat, w); grav = qri(quat, torch.tensor([0., 0., -1.], device=dev).expand(N, 3))
    return torch.cat([gyro, grav, Q(s0)[:, 7:] - default, QD(s0)[:, 6:], last, cmd], 1), bq, gyro

# ---------------------------------------------------------------- ตัวประมาณ + ตัวเดินตามเป้า (ใช้แต่ค่าประมาณ)
eid = torch.tensor([i // a.per for i in range(N)], device=dev)
gen = torch.Generator(device=dev).manual_seed(3)
bias = (torch.rand(N, device=dev, generator=gen) * 2 - 1) * math.radians(a.gbias)
ph = torch.zeros(N, 2, device=dev); yh = torch.zeros(N, device=dev)          # ตำแหน่ง/ทิศที่ "คิดว่า"
s = a.side
WP = torch.tensor([[s, 0], [s, s], [0, s], [0, 0]] * a.loops, device=dev, dtype=torch.float32)
if a.calib: WP = torch.tensor([[100.0, 0.0]], device=dev)
wpi = torch.zeros(N, dtype=torch.long, device=dev); done = torch.zeros(N, dtype=torch.bool, device=dev)
fell = torch.zeros(N, dtype=torch.bool, device=dev); t_done = torch.full((N,), float("nan"), device=dev)
K = torch.tensor([a.k if EST[int(e)] in ("gyro_cal", "gyro_still") else 1.0 for e in eid], device=dev)
use_gyro = torch.tensor([EST[int(e)] in ("gyro", "gyro_cal", "gyro_still") for e in eid], device=dev)
use_still = torch.tensor([EST[int(e)] == "gyro_still" for e in eid], device=dev)
still_sum = torch.zeros(N, device=dev); bias_hat = torch.zeros(N, device=dev)
trace = []; true_still = []

def gyro_meas(gyro): return gyro[:, 2] + bias + torch.randn(N, device=dev, generator=gen) * a.gnoise
def step_est(gyro):
    wz_meas = gyro_meas(gyro) - torch.where(use_still, bias_hat, 0.0)
    yh[:] = yh + torch.where(use_gyro, wz_meas, cmd[:, 2]) * 0.02
    v = cmd[:, 0] * K
    ph[:] = ph + torch.stack([torch.cos(yh), torch.sin(yh)], 1) * v[:, None] * 0.02

def control(t, bq):
    while True:
        adv = ~done & ((WP[wpi] - ph).norm(dim=1) < 0.05)
        if not adv.any(): break
        last_wp = adv & (wpi == len(WP) - 1); done[last_wp] = True; t_done[last_wp] = t
        wpi[adv & ~last_wp] += 1
    tv = WP[wpi] - ph; herr = torch.atan2(torch.sin(torch.atan2(tv[:, 1], tv[:, 0]) - yh), torch.cos(torch.atan2(tv[:, 1], tv[:, 0]) - yh))
    turn = herr.abs() > 0.15
    cmd[:, 0] = torch.where(done | fell | turn, 0.0, a.vx)
    cmd[:, 2] = torch.where(done | fell, 0.0, torch.where(turn, torch.sign(herr) * 0.6, (2.0 * herr).clamp(-0.6, 0.6)))
    x, y = bq[:, 3], bq[:, 4]; fell[(1 - 2 * (x * x + y * y)) < 0.55] = True

viewer = None
if a.video:
    import newton.viewer
    from PIL import Image
    W, H = map(int, a.res.split("x"))
    viewer = newton.viewer.ViewerGL(width=W, height=H, headless=True); viewer.set_model(model); viewer.set_world_offsets((0.0, 0.0, 0.0))
    viewer.set_camera(wp.vec3(s / 2, -1.25, 2.3), -55.0, 90.0); os.makedirs(a.video, exist_ok=True)

steps = int(a.secs * 50); t0 = time.time(); nf = 0
with torch.no_grad():
    for k in range(steps):
        t = k * 0.02
        obs, bq, gyro = obs_now(k)
        KS = int(a.still * 50)
        if KS // 2 <= k < KS: still_sum += gyro_meas(gyro); true_still.append(float(gyro[:, 2].abs().mean()))   # ครึ่งหลังของช่วงยืน
        if k == KS: bias_hat[:] = still_sum / (KS - KS // 2)
        if k >= KS:
            step_est(gyro); control(t, bq)
        if a.calib and t >= a.still + 12: break
        if bool((done | fell).all()) and t > 5: break
        obs[:, -13:] = cmd; act = policy(obs); last = act; tgt[:, TQ] = default + act
        wp.capture_launch(graph)
        if k % 25 == 0: trace.append(torch.cat([bq[:, :2], ph], 1).cpu().numpy())
        if viewer is not None and k % a.video_every == 0:
            viewer.begin_frame(t); viewer.log_state(s0); viewer.end_frame()
            Image.fromarray(viewer.get_frame().numpy()).save(f"{a.video}/f_{nf:04d}.png"); nf += 1
wall = time.time() - t0
bq = wp.to_torch(s0.body_q)[trunk]; p = bq[:, :2]
if a.calib:
    ok = ~fell; kk = float((p[ok, 0] / ph[ok, 0]).mean())
    print(json.dumps(dict(calib_k=round(kk, 3), true_m=round(float(p[ok, 0].mean()), 2), believed_m=round(float(ph[ok, 0].mean()), 2), n=int(ok.sum()))))
    raise SystemExit
err = (p - ph).norm(dim=1); home = p.norm(dim=1)
res = dict(still_s=a.still, true_gyro_while_still_deg_s=round(math.degrees(sum(true_still) / max(len(true_still), 1)), 3), bias_err_med_deg_s=round(math.degrees(float((bias_hat - bias)[use_still].abs().median())), 3) if use_still.any() else None, N=N, sim_s=round(t, 1), wall_s=round(wall, 1), side=s, loops=a.loops, k=a.k, gyro_bias_deg_s=a.gbias, groups={}, lanes=[])
for j, e in enumerate(EST):
    m = (eid == j) & ~fell & done
    res["groups"][e] = dict(n=a.per, finished=int(m.sum()), fell=int((fell & (eid == j)).sum()),
                            home_err_med=round(float(home[m].median()), 3) if m.any() else None, home_err_max=round(float(home[m].max()), 3) if m.any() else None)
for i in range(N):
    res["lanes"].append(dict(est=EST[int(eid[i])], x=round(float(p[i, 0]), 3), y=round(float(p[i, 1]), 3), fell=bool(fell[i]), done=bool(done[i])))
res["trace"] = np.stack(trace).round(3).tolist()
print(json.dumps({k: v for k, v in res.items() if k not in ("lanes", "trace")}, ensure_ascii=False))
if a.out: json.dump(res, open(a.out, "w"))
