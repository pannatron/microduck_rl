"""ส่งของในอพาร์ตเมนต์บน Newton: เป็ดแบกพัสดุบนหลัง เดินจากห้องหนึ่งไปอีกห้องผ่านประตูจริง หลายเลนพร้อมกัน

ฉากคือ src/.../apartment.xml ของ Pollen (6 ห้อง 8×6 ม., กำแพง 1.6 ม., เฟอร์นิเจอร์, ช่องบันไดในทางเดิน)
แต่ละเลน = world แยก · เลน = policy × น้ำหนักพัสดุ · ล้ม = ส่งไม่สำเร็จ (พัสดุตก) ไม่มีเกิดใหม่
วัด: สำเร็จกี่เลน, เวลา, งานกล (Σ|τ·q̇|dt จาก PD ที่ใช้จริง), ระยะทาง → พลังงานต่อเมตร

รันจาก ~/IsaacLab:
  .venv/bin/python ~/repos/microduck_rl/newton_port/newton_delivery.py --mission kitchen_bedroom \
      --policies velstand,rough_ft --payloads 0,50,100,150 --per 4
"""
import argparse, os, json, math, time
import numpy as np, torch, warp as wp, newton, mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.expanduser("~/repos/microduck_rl/src/mjlab_microduck/robot/microduck/")
# เส้นทาง (x, y) ในพิกัดของ apartment.xml — ผ่านกลางช่องประตู ห่างเฟอร์นิเจอร์ ≥ 15 ซม.
MISSIONS = {
    "kitchen_bedroom": dict(start=(-3.3, 1.9), route=[(-1.4, 2.0), (-1.0, 2.0), (-0.6, 2.0), (-0.3, 1.8), (0.5, 1.8), (0.9, 1.5)], goal=(1.25, 1.3)),
    "kitchen_office": dict(start=(-3.3, 1.9), route=[(-1.4, 2.0), (-1.0, 2.0), (-0.4, 1.7), (-0.2, 1.1), (-0.2, 0.3), (0.5, 0.3), (1.3, 0.35)], goal=(2.2, 0.4)),   # x -0.2: เลี่ยงโต๊ะ console (x ถึง -0.58)
    "living_bath": dict(start=(-2.0, -2.0), route=[(-1.5, -1.4), (-1.0, -1.4), (-0.7, -1.6), (-0.7, -2.1), (0.5, -2.1), (1.0, -2.1)], goal=(1.8, -2.2)),
}
ap = argparse.ArgumentParser()
ap.add_argument("--mission", default="kitchen_bedroom", choices=list(MISSIONS))
ap.add_argument("--policies", default="velstand,rough_ft")
ap.add_argument("--payloads", default="0,50,100,150")    # กรัม
ap.add_argument("--per", type=int, default=4)
ap.add_argument("--secs", type=float, default=120)
ap.add_argument("--lane", type=float, default=7.0)        # ห้องชุดกว้าง 6 ม. ในแกน y
ap.add_argument("--noise", type=float, default=0.03)
ap.add_argument("--pd-kd", dest="pd_kd", type=float, default=0.053)
ap.add_argument("--vx", type=float, default=0.3); ap.add_argument("--wzmin", type=float, default=0.5)
ap.add_argument("--goal-r", type=float, default=0.25)
ap.add_argument("--video", default=None); ap.add_argument("--video-every", type=int, default=5)
ap.add_argument("--cam", default="top:0")                  # top:<lane> | follow:<lane> | x,y,z,pitch,yaw
ap.add_argument("--res", default="1280x720")
ap.add_argument("--out", default=None)
a = ap.parse_args()
dev = "cuda:0"
MS = MISSIONS[a.mission]
POL = a.policies.split(","); PAY = [float(v) for v in a.payloads.split(",")]
GROUPS = [(p, g) for p in POL for g in PAY]                 # กลุ่มละ a.per เลน
N = len(GROUPS) * a.per

# ---------------------------------------------------------------- policies
nets = []
for name in POL:
    P = np.load(os.path.join(HERE, name + ".npz")); T = lambda k: torch.tensor(P[k], device=dev)
    nets.append(dict(mean=T("mean")[0], std=T("std")[0], layers=[(T(f"w{k}"), T(f"b{k}")) for k in range(4)], default=T("default_pose")))
default = nets[0]["default"]
pidx = torch.tensor([POL.index(GROUPS[i // a.per][0]) for i in range(N)], device=dev)
def policy(obs):
    out = torch.empty(N, 14, device=dev)
    for j, n in enumerate(nets):
        m = pidx == j
        if not m.any(): continue
        x = (obs[m] - n["mean"]) / n["std"]
        for k, (w, b) in enumerate(n["layers"]):
            x = x @ w.T + b
            if k < 3: x = torch.nn.functional.elu(x)
        out[m] = x
    return out

# ---------------------------------------------------------------- ฉาก: apartment.xml → Newton (ต่อ world)
mj = mujoco.MjModel.from_xml_path(f"{ROBOT}scene_apartment.xml")
def xf(pos, quat=(1, 0, 0, 0)): return wp.transform(wp.vec3(*map(float, pos)), wp.quat(float(quat[1]), float(quat[2]), float(quat[3]), float(quat[0])))
# Newton ไม่อ่าน texture ของ MuJoCo — ใช้สีเฉลี่ยของ texture พื้นแต่ละห้อง (rgb1/rgb2 ใน apartment.xml) แทน
FLOOR = {"kitchen": (0.74, 0.79, 0.71), "living": (0.62, 0.48, 0.28), "cor": (0.45, 0.42, 0.40), "corridor": (0.45, 0.42, 0.40),
         "bedroom": (0.61, 0.53, 0.72), "office": (0.73, 0.48, 0.39), "bath": (0.71, 0.82, 0.88)}
def color(g):
    name = mujoco.mj_id2name(mj, mujoco.mjtObj.mjOBJ_GEOM, g) or ""
    if name.startswith("floor_") and mj.geom_contype[g] == 0:
        key = name[6:].rsplit("_", 1)[0] if name[6:] not in FLOOR else name[6:]
        if key in FLOOR: return wp.vec3(*FLOOR[key])
    if name in ("floor_w", "floor_e") or name.startswith("floor_corridor"): return wp.vec3(0.40, 0.40, 0.42)
    m = mj.geom_matid[g]; c = mj.mat_rgba[m] if m >= 0 else mj.geom_rgba[g]
    if name.startswith(("wall_", "wA", "wB", "wC", "wF", "wG")): c = (0.86, 0.85, 0.82)
    return wp.vec3(*map(float, c[:3]))
def apartment(b):
    n = 0
    for g in range(mj.ngeom):
        if mj.geom_bodyid[g] != 0: continue
        typ, s = mj.geom_type[g], mj.geom_size[g]
        cfg = newton.ModelBuilder.ShapeConfig(mu=1.0)
        if mj.geom_contype[g] == 0 and mj.geom_conaffinity[g] == 0: cfg.has_shape_collision = False
        pos = mj.geom_pos[g].copy()
        if not cfg.has_shape_collision and (mujoco.mj_id2name(mj, mujoco.mjtObj.mjOBJ_GEOM, g) or "").startswith(("floor_", "rug_")): pos[2] += 0.0045   # ยกพื้นสีขึ้นเหนือพื้นชน (ไม่งั้นจมอยู่ใต้)
        t = xf(pos, mj.geom_quat[g]); kw = dict(xform=t, cfg=cfg, color=color(g), label=mujoco.mj_id2name(mj, mujoco.mjtObj.mjOBJ_GEOM, g))
        if typ == mujoco.mjtGeom.mjGEOM_BOX: b.add_shape_box(-1, hx=float(s[0]), hy=float(s[1]), hz=float(s[2]), **kw)
        elif typ == mujoco.mjtGeom.mjGEOM_CYLINDER: b.add_shape_cylinder(-1, radius=float(s[0]), half_height=float(s[1]), **kw)
        elif typ == mujoco.mjtGeom.mjGEOM_SPHERE: b.add_shape_sphere(-1, radius=float(s[0]), **kw)
        else: continue
        n += 1
    return n

h0 = math.atan2(MS["route"][0][1] - MS["start"][1], MS["route"][0][0] - MS["start"][0])
scene = newton.ModelBuilder()
for i in range(N):                      # แต่ละเลนน้ำหนักพัสดุต่างกัน → สร้าง builder ต่อกลุ่ม แล้วเพิ่มเป็น world
    duck = newton.ModelBuilder()
    duck.add_mjcf(f"{ROBOT}robot_groundcontact.xml", floating=True, parse_visuals=True, enable_self_collisions=False)
    nd_duck, nq_duck = duck.joint_dof_count, duck.joint_coord_count
    for j in range(6, nd_duck):
        duck.joint_effort_limit[j] = 0.96; duck.joint_target_kd[j] = a.pd_kd
    duck.joint_q[0:7] = [MS["start"][0], MS["start"][1], 0.13, 0, 0, math.sin(h0 / 2), math.cos(h0 / 2)]
    duck.joint_q[7:nq_duck] = default.cpu().tolist()
    TQ = slice(7, nq_duck) if len(duck.joint_target_q) == duck.joint_coord_count else slice(6, nd_duck)
    duck.joint_target_q[TQ] = default.cpu().tolist()
    grams = GROUPS[i // a.per][1]
    # กล่องพัสดุ 8×6×4 ซม. บนหลัง (ไม่ชนอะไร มีแต่มวล) — ทุกเลนต้องมี shape เท่ากัน (SolverMuJoCo บังคับ) จึงใส่กล่องซ่อนมวล ~0 ให้เลน 0 g
    hx, hy, hz = 0.04, 0.03, 0.02; cfg = newton.ModelBuilder.ShapeConfig(density=max(grams, 1e-3) / 1000 / (8 * hx * hy * hz))
    cfg.has_shape_collision = False; cfg.is_visible = grams > 0
    duck.add_shape_box(0, xform=xf((-0.035, 0.0, 0.035)), hx=hx, hy=hy, hz=hz, cfg=cfg, color=wp.vec3(0.78, 0.55, 0.30), label="parcel")
    if grams > 0:   # MJCF ล็อก inertia ของ trunk ไว้ → shape ใหม่ไม่เพิ่มมวลเอง: รวมมวล/CoM/inertia ของกล่องเข้า trunk ด้วยมือ
        m0, mp = duck.body_mass[0], grams / 1000; c0 = np.array(duck.body_com[0]); cp = np.array([-0.035, 0.0, 0.035])
        c = (m0 * c0 + mp * cp) / (m0 + mp)
        def shift(I, m, r): return I + m * (np.dot(r, r) * np.eye(3) - np.outer(r, r))
        Ibox = mp / 12 * np.diag([(2 * hy) ** 2 + (2 * hz) ** 2, (2 * hx) ** 2 + (2 * hz) ** 2, (2 * hx) ** 2 + (2 * hy) ** 2])
        I = shift(np.array(duck.body_inertia[0], dtype=float).reshape(3, 3), m0, c0 - c) + shift(Ibox, mp, cp - c)
        duck.body_mass[0] = m0 + mp; duck.body_inv_mass[0] = 1 / (m0 + mp); duck.body_com[0] = wp.vec3(*c)
        duck.body_inertia[0] = wp.mat33(*I.flatten()); duck.body_inv_inertia[0] = wp.mat33(*np.linalg.inv(I).flatten())
    nstat = apartment(duck)
    scene.add_world(duck, xform=wp.transform(wp.vec3(0.0, a.lane * i, 0.0), wp.quat_identity()))
model = scene.finalize(device=dev)
ND, NQ = model.joint_dof_count // N, model.joint_coord_count // N
NB = model.body_count // N
solver = newton.solvers.SolverMuJoCo(model, iterations=10, ls_iterations=50, integrator="euler", nconmax=200, njmax=800)
s0, s1, ctrl = model.state(), model.state(), model.control()
newton.eval_fk(model, model.joint_q, model.joint_qd, s0)
Q = lambda st: wp.to_torch(st.joint_q).view(N, NQ); QD = lambda st: wp.to_torch(st.joint_qd).view(N, ND)
torch.manual_seed(0)
Q(s0)[:, 7:nq_duck] += (torch.rand(N, 14, device=dev) * 2 - 1) * a.noise
newton.eval_fk(model, s0.joint_q, s0.joint_qd, s0)
tgt = wp.to_torch(ctrl.joint_target_q).view(N, -1)
tgt[:, TQ] = default
ke_all = wp.to_torch(model.joint_target_ke).view(N, -1)
KE = ke_all[:, TQ] if ke_all.shape[1] == NQ else ke_all[:, 6:nd_duck]          # kp ของ PD ต่อข้อต่อ
trunk = torch.arange(N, device=dev) * NB
origin = wp.to_torch(s0.body_q)[trunk][:, :2].clone() - torch.tensor(MS["start"], device=dev)
SUB, dt = 4, 0.005

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

# ---------------------------------------------------------------- ภารกิจ (tensor)
WP = torch.tensor(MS["route"] + [MS["goal"]], device=dev); GOAL = torch.tensor(MS["goal"], device=dev)
wpi = torch.zeros(N, dtype=torch.long, device=dev)
state = torch.zeros(N, dtype=torch.long, device=dev)          # 0 กำลังไป · 1 ส่งสำเร็จ · 2 ล้ม (พัสดุตก)
t_end = torch.full((N,), float("nan"), device=dev); work = torch.zeros(N, device=dev); dist = torch.zeros(N, device=dev)
tilt_t = torch.full((N,), -1.0, device=dev); prev_p = None; fall_xy = torch.full((N, 2), float("nan"), device=dev)

def game(t, bq):
    global prev_p
    p = bq[:, :2] - origin; x, y, zq, w = bq[:, 3], bq[:, 4], bq[:, 5], bq[:, 6]
    run = state == 0
    if prev_p is None or round(t / 0.02) % 25 == 0:               # ระยะทางวัดทุก 0.5 s — ไม่นับการส่ายของลำตัวทุกก้าว
        if prev_p is not None: dist[run] += (p - prev_p).norm(dim=1)[run]
        prev_p = p.clone()
    done = run & ((p - GOAL).norm(dim=1) < a.goal_r); state[done] = 1; t_end[done] = t
    up = 1 - 2 * (x * x + y * y); tilted = run & ((up < 0.55) | (bq[:, 2] < 0.04))
    tilt_t[tilted & (tilt_t < 0)] = t; tilt_t[~tilted] = -1
    fl = tilted & (t - tilt_t > 0.5); state[fl] = 2; t_end[fl] = t; fall_xy[fl] = p[fl]
    run = state == 0
    while True:
        adv = run & (wpi < len(WP) - 1) & ((WP[wpi] - p).norm(dim=1) < 0.12)
        if not adv.any(): break
        wpi[adv] += 1
    tv = WP[wpi] - p; yaw = torch.atan2(2 * (w * zq + x * y), 1 - 2 * (y * y + zq * zq))
    herr = torch.atan2(torch.sin(torch.atan2(tv[:, 1], tv[:, 0]) - yaw), torch.cos(torch.atan2(tv[:, 1], tv[:, 0]) - yaw))
    near = (GOAL - p).norm(dim=1) < 0.5
    v = torch.where(near, 0.2, a.vx) * torch.cos(herr).clamp(min=0) * (herr.abs() < 0.8)
    wz = (2.5 * herr).clamp(-1, 1); wz = torch.where(herr.abs() > 0.08, torch.sign(herr) * torch.maximum(wz.abs(), torch.tensor(a.wzmin, device=dev)), wz)
    cmd[:, 0] = torch.where(run, v, 0.0); cmd[:, 2] = torch.where(run, wz, 0.0)

# ---------------------------------------------------------------- viewer
viewer = None
if a.video:
    import newton.viewer
    from PIL import Image
    W, H = map(int, a.res.split("x"))
    viewer = newton.viewer.ViewerGL(width=W, height=H, headless=True); viewer.set_model(model)
    viewer.set_world_offsets((0.0, 0.0, 0.0))
    os.makedirs(a.video, exist_ok=True)
    def cam(bq):
        kind, _, arg = a.cam.partition(":")
        if kind == "top":
            oy = float(origin[int(arg), 1]); viewer.set_camera(wp.vec3(0.0, oy - 3.4, 8.2), -66.0, 90.0)
        elif kind == "follow":
            i = int(arg); fx, fy, fz = (float(v) for v in bq[i, :3])
            viewer.set_camera(wp.vec3(fx - 0.5, fy - 0.7, fz + 0.75), -42.0, 55.0)
        else:
            cx, cy, cz, cp_, cy_ = map(float, a.cam.split(",")); viewer.set_camera(wp.vec3(cx, cy, cz), cp_, cy_)

steps = int(a.secs * 50); torch.cuda.synchronize(); t0 = time.time(); nf = 0
with torch.no_grad():
    for k in range(steps):
        t = k * 0.02
        obs, bq = obs_now(k); game(t, bq)
        if not (state == 0).any() and (viewer is None or t > float(t_end.max()) + 2): break
        obs[:, -13:] = cmd
        act = policy(obs); last = act
        tgt[:, TQ] = default + act
        q, qd = Q(s0)[:, 7:nq_duck], QD(s0)[:, 6:nd_duck]
        tau = (KE * (tgt[:, TQ] - q) - a.pd_kd * qd).clamp(-0.96, 0.96)        # แรงบิดที่ PD สั่งจริง (ประมาณจาก state ต้น step)
        work += torch.where(state == 0, (tau * qd).abs().sum(1) * 0.02, 0.0)
        wp.capture_launch(graph)
        if viewer is not None and k % a.video_every == 0:
            cam(wp.to_torch(s0.body_q)[trunk]); viewer.begin_frame(t); viewer.log_state(s0); viewer.end_frame()
            Image.fromarray(viewer.get_frame().numpy()).save(f"{a.video}/f_{nf:04d}.png"); nf += 1
torch.cuda.synchronize(); wall = time.time() - t0

res = dict(mission=a.mission, N=N, sim_s=round(t, 1), wall_s=round(wall, 1), static_shapes=nstat, route_m=round(float(sum(math.dist(u, v) for u, v in zip([MS["start"]] + MS["route"], MS["route"] + [MS["goal"]]))), 2), lanes=[], groups={})
for i in range(N):
    pol, g = GROUPS[i // a.per]
    res["lanes"].append(dict(policy=pol, grams=g, state=["running", "delivered", "fell"][int(state[i])], t=None if math.isnan(float(t_end[i])) else round(float(t_end[i]), 1),
                             work_J=round(float(work[i]), 2), dist_m=round(float(dist[i]), 2), wp=int(wpi[i]),
                             fall_xy=None if math.isnan(float(fall_xy[i, 0])) else [round(float(v), 2) for v in fall_xy[i]]))
for pol, g in GROUPS:
    L = [l for l in res["lanes"] if l["policy"] == pol and l["grams"] == g]; ok = [l for l in L if l["state"] == "delivered"]
    res["groups"][f"{pol}@{g:g}g"] = dict(delivered=len(ok), n=len(L), fell=sum(l["state"] == "fell" for l in L),
                                          t_med=sorted(l["t"] for l in ok)[len(ok) // 2] if ok else None,
                                          J_per_m=round(sum(l["work_J"] for l in ok) / max(sum(l["dist_m"] for l in ok), 1e-6), 2) if ok else None)
print(json.dumps({k: v for k, v in res.items() if k != "lanes"}, ensure_ascii=False))
if a.out: json.dump(res, open(a.out, "w"), ensure_ascii=False, indent=1)
