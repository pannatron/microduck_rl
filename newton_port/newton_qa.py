"""QA ก่อนปล่อย policy: เป็ด ~1,000 ตัวบน Newton ทดสอบพร้อมกัน — policy × เงื่อนไข × ซ้ำ แล้วออกตารางผ่าน/ไม่ผ่าน

ทุกตัวเดินตรง vx 0.3 m/s นาน 20 s · ผ่าน = ไม่ล้ม และเดินได้ ≥ 1.5 ม.
เงื่อนไข (ตั้งต่อ world ก่อนสร้าง solver):
  nominal    ปกติ (พื้น plane)
  box        พื้นเป็นกล่อง — mesh ของเท้าชนกล่องด้วย CCD ไม่ใช่สูตร mesh-plane (terrain Rough ของ mjlab เป็นกล่องทั้งหมด)
  push05     โดนผลักด้านข้าง 0.5 m/s ที่ 5, 10, 15 s (ทิศสุ่ม)
  push10     โดนผลัก 1.0 m/s (เพดานที่ Pollen ใช้เทรน velstand)
  ice        พื้นลื่น μ = 0.3 (ปกติ 1.0) — พื้นแยกต่อ world เพราะ MuJoCo ใช้ μ ที่มากกว่าของสองผิว
  weak       แรงบิดสูงสุด ×0.85 (≈ แบต 6.3 V จาก 7.4 V)
  heavy      แบกของ 200 g บนหลัง
  imu        gyro noise σ 0.2 rad/s + gravity noise σ 0.05 ใน obs

รันจาก ~/IsaacLab:
  .venv/bin/python ~/repos/microduck_rl/newton_port/newton_qa.py --reps 24 --out qa.json
"""
import argparse, os, json, math, time
import numpy as np, torch, warp as wp, newton

HERE = os.path.dirname(os.path.abspath(__file__))
XML = os.path.expanduser("~/repos/microduck_rl/src/mjlab_microduck/robot/microduck/robot_groundcontact.xml")
ap = argparse.ArgumentParser()
ap.add_argument("--policies", default="walk_2000,rough_ft,velstand,climb35,newton_walk_2000,newton_latency_2000")
ap.add_argument("--tests", default="nominal,box,push05,push10,ice,weak,heavy,imu")
ap.add_argument("--reps", type=int, default=24)
ap.add_argument("--secs", type=float, default=20)
ap.add_argument("--vx", type=float, default=0.3)
ap.add_argument("--pd-kd", dest="pd_kd", type=float, default=0.053)
ap.add_argument("--noise", type=float, default=0.03)
ap.add_argument("--video", default=None); ap.add_argument("--video-every", type=int, default=3); ap.add_argument("--res", default="1280x720")
ap.add_argument("--cam", default="0,0,0,-30,45")
ap.add_argument("--ice-mu", dest="ice_mu", type=float, default=0.3)
ap.add_argument("--weak", type=float, default=0.85)
ap.add_argument("--plane", action="store_true")
ap.add_argument("--kp", type=float, default=None)   # แทน kp ของ MJCF (สัปดาห์ 9: PD ที่ฟิตกับ BAM = 0.695)
ap.add_argument("--tau", type=float, default=0.96)  # แรงบิดสูงสุด (ฟิต BAM = 0.79)      # พื้น ground plane ร่วม (ไม่มีโหมด ice) — ไว้เทียบ
ap.add_argument("--out", default=None)
a = ap.parse_args()
dev = "cuda:0"
POL, TST = a.policies.split(","), a.tests.split(",")
R = a.reps; N = len(POL) * len(TST) * R
pol_of = torch.tensor([i // (len(TST) * R) for i in range(N)], device=dev)
tst_of = torch.tensor([(i // R) % len(TST) for i in range(N)], device=dev)
def is_t(name): return tst_of == TST.index(name) if name in TST else torch.zeros(N, dtype=torch.bool, device=dev)

nets = []
for name in POL:
    P = np.load(os.path.join(HERE, name + ".npz")); T = lambda k: torch.tensor(P[k], device=dev)
    nets.append(dict(mean=T("mean")[0], std=T("std")[0], layers=[(T(f"w{k}"), T(f"b{k}")) for k in range(4)], default=T("default_pose")))
default = nets[0]["default"]
def policy(obs):
    outs = []
    for n in nets:
        x = (obs - n["mean"]) / n["std"]
        for k, (w, b) in enumerate(n["layers"]):
            x = x @ w.T + b
            if k < 3: x = torch.nn.functional.elu(x)
        outs.append(x)
    return torch.stack(outs)[pol_of, torch.arange(N, device=dev)]

# ---------------------------------------------------------------- เป็ด + พื้นของตัวเอง (ต่อ world)
duck = newton.ModelBuilder()
duck.add_mjcf(XML, floating=True, parse_visuals=bool(a.video), enable_self_collisions=False)
nd, nq = duck.joint_dof_count, duck.joint_coord_count
for i in range(6, nd):
    duck.joint_effort_limit[i] = a.tau; duck.joint_target_kd[i] = a.pd_kd
    if a.kp is not None: duck.joint_target_ke[i] = a.kp
duck.joint_q[0:7] = [0, 0, 0.125, 0, 0, 0, 1]; duck.joint_q[7:] = default.cpu().tolist()
TQ = slice(7, nq) if len(duck.joint_target_q) == nq else slice(6, nd)
duck.joint_target_q[TQ] = default.cpu().tolist()
if not a.plane:                                         # ทุก world มีทั้ง plane และกล่อง (SolverMuJoCo ต้องการ shape เท่ากัน) — เลือกอันที่อยู่ระดับพื้นทีหลัง
    duck.add_shape_plane(plane=(0.0, 0.0, 1.0, 0.0), width=0.0, length=0.0, cfg=newton.ModelBuilder.ShapeConfig(mu=1.0), color=wp.vec3(0.32, 0.34, 0.38), label="floor_plane")
    duck.add_shape_box(-1, xform=wp.transform(wp.vec3(4.0, 0.0, -1.05), wp.quat_identity()), hx=6.0, hy=6.0, hz=0.05,
                       cfg=newton.ModelBuilder.ShapeConfig(mu=1.0), color=wp.vec3(0.30, 0.33, 0.40), label="floor_box")
scene = newton.ModelBuilder(); scene.replicate(duck, N, spacing=(0.0, 0.0, 0.0))
if a.plane: scene.add_ground_plane()
model = scene.finalize(device=dev)
NB = duck.body_count
# ---- เงื่อนไขต่อ world (แก้ model ก่อนสร้าง solver)
sw = wp.to_torch(model.shape_world); mu = wp.to_torch(model.shape_material_mu)
if not a.plane:                                         # world ที่ทดสอบพื้นกล่อง: ยกกล่องขึ้นมาที่ z = 0 แล้วเอา plane ลงไปใต้
    lab = model.shape_label; xf_ = wp.to_torch(model.shape_transform)
    pl = torch.tensor([i for i, l in enumerate(lab) if l.endswith("floor_plane")], device=dev); bx = torch.tensor([i for i, l in enumerate(lab) if l.endswith("floor_box")], device=dev)
    box_w = is_t("box") | (os.environ.get("BOXALL") == "1")
    xf_[bx[box_w[sw[bx].long()]], 2] = -0.05; xf_[pl[box_w[sw[pl].long()]], 2] = -2.0
ice_w = torch.nonzero(is_t("ice")).flatten()
mu[torch.isin(sw, ice_w)] = a.ice_mu
eff = wp.to_torch(model.joint_effort_limit).view(N, -1)
eff[is_t("weak"), 6:] *= a.weak
hv = torch.nonzero(is_t("heavy")).flatten() * NB                         # trunk ของ world ที่แบกของ
bm, bim = wp.to_torch(model.body_mass), wp.to_torch(model.body_inv_mass)
bc, bI, biI = wp.to_torch(model.body_com), wp.to_torch(model.body_inertia), wp.to_torch(model.body_inv_inertia)
if len(hv):
    m0, mp = bm[hv[0]].item(), 0.2; c0 = bc[hv[0]].clone(); cp = torch.tensor([-0.035, 0.0, 0.035], device=dev)
    c = (m0 * c0 + mp * cp) / (m0 + mp)
    def shift(I, m, r): return I + m * (torch.dot(r, r) * torch.eye(3, device=dev) - torch.outer(r, r))
    hx, hy, hz = 0.04, 0.03, 0.02
    Ib = mp / 12 * torch.diag(torch.tensor([(2 * hy) ** 2 + (2 * hz) ** 2, (2 * hx) ** 2 + (2 * hz) ** 2, (2 * hx) ** 2 + (2 * hy) ** 2], device=dev))
    I = shift(bI[hv[0]].view(3, 3), m0, c0 - c) + shift(Ib, mp, cp - c)
    bm[hv] = m0 + mp; bim[hv] = 1 / (m0 + mp); bc[hv] = c; bI[hv] = I.flatten() if bI.dim() == 2 else I; biI[hv] = torch.linalg.inv(I).flatten() if biI.dim() == 2 else torch.linalg.inv(I)
solver = newton.solvers.SolverMuJoCo(model, iterations=int(os.environ.get("ITERS", 10)), ls_iterations=50, integrator="euler", nconmax=int(os.environ.get("NCONMAX", 64)), njmax=int(os.environ.get("NJMAX", 256)))
s0, s1, ctrl = model.state(), model.state(), model.control()
newton.eval_fk(model, model.joint_q, model.joint_qd, s0)
Q = lambda st: wp.to_torch(st.joint_q).view(N, nq); QD = lambda st: wp.to_torch(st.joint_qd).view(N, nd)
torch.manual_seed(0)
Q(s0)[:, 7:] += (torch.rand(N, 14, device=dev) * 2 - 1) * a.noise
newton.eval_fk(model, s0.joint_q, s0.joint_qd, s0)
tgt = wp.to_torch(ctrl.joint_target_q).view(N, -1); tgt[:, TQ] = default
trunk = torch.arange(N, device=dev) * NB
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
gen = torch.Generator(device=dev).manual_seed(5)
imu_w = is_t("imu")
def obs_now(k):
    bq = wp.to_torch(s0.body_q)[trunk]
    src_q, src_qd = (bq_lag, bqd_lag) if k > 0 else (s0.body_q, s0.body_qd)
    quat = wp.to_torch(src_q)[trunk][:, 3:7]; w = wp.to_torch(src_qd)[trunk][:, 3:6]
    gyro = qri(quat, w); grav = qri(quat, torch.tensor([0., 0., -1.], device=dev).expand(N, 3))
    gyro = gyro + imu_w[:, None] * torch.randn(N, 3, device=dev, generator=gen) * 0.2
    grav = grav + imu_w[:, None] * torch.randn(N, 3, device=dev, generator=gen) * 0.05
    return torch.cat([gyro, grav, Q(s0)[:, 7:] - default, QD(s0)[:, 6:], last, cmd], 1), bq

push_mag = torch.where(is_t("push05"), 0.5, torch.where(is_t("push10"), 1.0, 0.0))
fell = torch.zeros(N, dtype=torch.bool, device=dev); t_fall = torch.full((N,), float("nan"), device=dev)
p_start = None

viewer = None
if a.video:
    import newton.viewer
    from PIL import Image
    W, H = map(int, a.res.split("x"))
    if not a.plane:                                     # พื้นทุก world ซ้อนกันในภาพ (กระพริบ) → โชว์แค่ plane ของ world 0
        fl = model.shape_flags.numpy(); VIS = int(newton.ShapeFlags.VISIBLE); swn = model.shape_world.numpy()
        for i, l in enumerate(model.shape_label):
            if (l.endswith("floor_plane") and swn[i] != 0) or l.endswith("floor_box"): fl[i] &= ~VIS
        model.shape_flags.assign(fl)
    viewer = newton.viewer.ViewerGL(width=W, height=H, headless=True); viewer.set_model(model)
    viewer.set_world_offsets((float(os.environ.get('GRID', 0.9)), float(os.environ.get('GRID', 0.9)), 0.0))   # วางเป็ดทุก world เป็นตาราง (ภาพเท่านั้น)
    cx, cy, cz, cp_, cy_ = map(float, a.cam.split(","))
    os.makedirs(a.video, exist_ok=True)

steps = int(a.secs * 50); torch.cuda.synchronize(); t0 = time.time(); nf = 0
with torch.no_grad():
    for k in range(steps):
        t = k * 0.02
        obs, bq = obs_now(k)
        if k == 50: p_start = bq[:, :2].clone()
        cmd[:, 0] = torch.where((k >= 50) & ~fell, a.vx, 0.0)
        if k in (250, 500, 750):                         # ผลักที่ 5, 10, 15 s: ความเร็วแนวนอนทิศสุ่ม (ตั้งทับ แบบ push_by_setting_velocity)
            ang = torch.rand(N, device=dev, generator=gen) * 2 * math.pi
            m = push_mag > 0
            QD(s0)[m, 0] = (push_mag * torch.cos(ang))[m]; QD(s0)[m, 1] = (push_mag * torch.sin(ang))[m]
        x, y = bq[:, 3], bq[:, 4]; tilted = ((1 - 2 * (x * x + y * y)) < 0.55) | (bq[:, 2] < 0.05)
        newf = tilted & ~fell; fell |= tilted; t_fall[newf] = t
        obs[:, -13:] = cmd; act = policy(obs); last = act; tgt[:, TQ] = default + act
        wp.capture_launch(graph)
        if viewer is not None and k % a.video_every == 0:
            viewer.set_camera(wp.vec3(cx, cy, cz), cp_, cy_); viewer.begin_frame(t); viewer.log_state(s0); viewer.end_frame()
            Image.fromarray(viewer.get_frame().numpy()).save(f"{a.video}/f_{nf:04d}.png"); nf += 1
torch.cuda.synchronize(); wall = time.time() - t0
bq = wp.to_torch(s0.body_q)[trunk]; dist = (bq[:, :2] - p_start).norm(dim=1)
ok = ~fell & (dist >= 1.5)
res = dict(N=N, reps=R, sim_s=a.secs, wall_s=round(wall, 1), policies=POL, tests=TST, cells={})
for i, pn in enumerate(POL):
    for j, tn in enumerate(TST):
        m = (pol_of == i) & (tst_of == j)
        res["cells"][f"{pn}|{tn}"] = dict(pass_=int(ok[m].sum()), n=int(m.sum()), fell=int(fell[m].sum()),
                                          dist_med=round(float(dist[m & ~fell].median()), 2) if (m & ~fell).any() else None,
                                          t_fall=sorted(round(float(v), 2) for v in t_fall[m & fell]))
print(json.dumps(dict(N=N, wall_s=res["wall_s"])))
for pn in POL: print(f"{pn:22s}", " ".join(f"{res['cells'][f'{pn}|{tn}']['pass_']:3d}" for tn in TST))
if a.out: json.dump(res, open(a.out, "w"), indent=1)
