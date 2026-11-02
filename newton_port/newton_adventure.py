"""Duck Adventure บน Newton: หลายเลน (world) วิ่งด่านเดียวกันพร้อมกันบน GPU — ฟิสิกส์ + ภาพจาก Newton ทั้งหมด

ด่านอ่านจาก MJCF ที่ playground/make_adventure.py สร้าง (กล่อง/ทรงกระบอก/ประตูบานพับ) แล้วสร้างใหม่ใน Newton ModelBuilder
กติกาเหมือน playground/ctl_adventure.py แต่ทำเป็น tensor: checkpoint, ล้ม/ตกลาวา → เกิดใหม่, autopilot ตาม waypoint

รันจาก ~/IsaacLab:
  .venv/bin/python ~/repos/microduck_rl/newton_port/newton_adventure.py --level adv20 --policies walk_2000,rough_ft,velstand --per 4 \
      --video /tmp/adv_frames --cam overview
"""
import argparse, os, json, math, time
import numpy as np, torch, warp as wp, newton, mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.expanduser("~/repos/microduck_rl/src/mjlab_microduck/robot/microduck/")
ap = argparse.ArgumentParser()
ap.add_argument("--level", default="adv20")
ap.add_argument("--policies", default="walk_2000,rough_ft,velstand")
ap.add_argument("--per", type=int, default=4)              # เลนต่อ policy (ต่างกันที่ท่าเริ่มสุ่ม ±noise)
ap.add_argument("--secs", type=float, default=180)
ap.add_argument("--lane", type=float, default=1.3)         # ระยะห่างเลน (ม.) — ด่านกว้าง ±0.5
ap.add_argument("--noise", type=float, default=0.03)
ap.add_argument("--pd-kd", dest="pd_kd", type=float, default=0.053)   # ค่าที่ตรงกับตอนเทรน (บทเรียนสัปดาห์ 6)
ap.add_argument("--vx", type=float, default=0.4); ap.add_argument("--vslow", type=float, default=0.3); ap.add_argument("--wzmin", type=float, default=0.5)
ap.add_argument("--vstairs", type=float, default=None)   # ความเร็วเฉพาะช่วงขึ้นบันได (ค่าเริ่มต้น = vslow)
# เลนแบบสลับท่าตามโซน: "rough_ft+velstand@mountain" = ใช้ rough_ft ทั้งด่าน ยกเว้นช่วงภูเขา (ตีนบันได → ปลายทางลาด) ใช้ velstand
ap.add_argument("--video", default=None); ap.add_argument("--video-every", type=int, default=5)
ap.add_argument("--cam", default="overview")              # overview | follow:<lane> | x,y,z,pitch,yaw
ap.add_argument("--res", default="1280x720")
ap.add_argument("--out", default=None)
a = ap.parse_args()
dev = "cuda:0"
RULES = json.load(open(f"{ROBOT}scene_{a.level}.json"))
POL = a.policies.split(",")                     # ชื่อเลน (spec) ตามลำดับ
N = len(POL) * a.per

# ---------------------------------------------------------------- policies (MLP ใน torch) + การสลับตามโซน
def parse(spec):
    if "+" not in spec: return spec, spec, None
    base, rest = spec.split("+"); alt, zone = rest.split("@"); return base, alt, zone
LANES = [parse(s) for s in POL]
NAMES = sorted({n for b, al, _ in LANES for n in (b, al)})
nets = []
for name in NAMES:
    P = np.load(os.path.join(HERE, name + ".npz")); T = lambda k: torch.tensor(P[k], device=dev)
    nets.append(dict(mean=T("mean")[0], std=T("std")[0], layers=[(T(f"w{k}"), T(f"b{k}")) for k in range(4)], default=T("default_pose")))
default = nets[0]["default"]
base_idx = torch.tensor([NAMES.index(LANES[i // a.per][0]) for i in range(N)], device=dev)
alt_idx = torch.tensor([NAMES.index(LANES[i // a.per][1]) for i in range(N)], device=dev)
active = base_idx.clone()                       # policy ที่คุมเลนนั้นอยู่ตอนนี้ (อัปเดตทุก step ตามโซน)
def policy(obs):
    outs = []
    for n in nets:
        x = (obs - n["mean"]) / n["std"]
        for k, (w, b) in enumerate(n["layers"]):
            x = x @ w.T + b
            if k < 3: x = torch.nn.functional.elu(x)
        outs.append(x)
    return torch.stack(outs)[active, torch.arange(N, device=dev)]

# ---------------------------------------------------------------- ด่าน: อ่าน geom ทุกชิ้นที่ไม่ใช่ตัวเป็ดจาก MJCF
mj = mujoco.MjModel.from_xml_path(f"{ROBOT}scene_{a.level}.xml")
COURSE = ("cone", "lava", "bridge", "stair", "ramp", "rock", "wall", "CP", "FINISH", "flag")
def mjname(t, i): return mujoco.mj_id2name(mj, t, i) or ""
def xf(pos, quat): return wp.transform(wp.vec3(*map(float, pos)), wp.quat(float(quat[1]), float(quat[2]), float(quat[3]), float(quat[0])))

duck = newton.ModelBuilder()
duck.add_mjcf(f"{ROBOT}robot_groundcontact.xml", floating=True, parse_visuals=True, enable_self_collisions=False)
nd_duck, nq_duck = duck.joint_dof_count, duck.joint_coord_count          # 20, 21
for i in range(6, nd_duck):
    duck.joint_effort_limit[i] = 0.96; duck.joint_target_kd[i] = a.pd_kd
duck.joint_q[0:7] = [0, 0, 0.125, 0, 0, 0, 1]
duck.joint_q[7:nq_duck] = nets[0]["default"].cpu().tolist()
TQ = slice(7, nq_duck) if len(duck.joint_target_q) == duck.joint_coord_count else slice(6, nd_duck)   # joint_target_q เป็น layout แบบ coord หรือ dof แล้วแต่รุ่น
duck.joint_target_q[TQ] = nets[0]["default"].cpu().tolist()

def add_geom(b, body, g, pos=None, quat=None):
    name = mjname(mujoco.mjtObj.mjOBJ_GEOM, g); typ = mj.geom_type[g]; s = mj.geom_size[g]; rgba = mj.geom_rgba[g]
    cfg = newton.ModelBuilder.ShapeConfig(mu=1.0)
    if mj.geom_contype[g] == 0 and mj.geom_conaffinity[g] == 0: cfg.has_shape_collision = False
    t = xf(mj.geom_pos[g] if pos is None else pos, mj.geom_quat[g] if quat is None else quat)
    col = wp.vec3(*map(float, rgba[:3]))
    if typ == mujoco.mjtGeom.mjGEOM_BOX: b.add_shape_box(body, xform=t, hx=float(s[0]), hy=float(s[1]), hz=float(s[2]), cfg=cfg, color=col, label=name)
    elif typ == mujoco.mjtGeom.mjGEOM_CYLINDER: b.add_shape_cylinder(body, xform=t, radius=float(s[0]), half_height=float(s[1]), cfg=cfg, color=col, label=name)

nstat = 0
for g in range(mj.ngeom):
    if mj.geom_bodyid[g] == 0 and mjname(mujoco.mjtObj.mjOBJ_GEOM, g).startswith(COURSE):
        add_geom(duck, -1, g); nstat += 1
# ประตูบานพับ: body + revolute joint + สปริงดึงปิด (target 0, ke จาก stiffness ใน MJCF)
doors = []
for bid in range(mj.nbody):
    bn = mjname(mujoco.mjtObj.mjOBJ_BODY, bid)
    if not bn.startswith("gate"): continue
    j = mj.body_jntadr[bid]; lo, hi = mj.jnt_range[j]
    body = duck.add_link(xform=xf(mj.body_pos[bid], [1, 0, 0, 0]), label=bn)
    for g in range(mj.body_geomadr[bid], mj.body_geomadr[bid] + mj.body_geomnum[bid]):
        add_geom(duck, body, g)
        duck.body_mass[body] = float(mj.body_mass[bid])
    jid = duck.add_joint_revolute(-1, body, parent_xform=xf(mj.body_pos[bid], [1, 0, 0, 0]), axis=(0, 0, 1), target_pos=0.0,
                                  target_ke=float(mj.jnt_stiffness[j]), target_kd=float(mj.dof_damping[mj.jnt_dofadr[j]]), limit_lower=float(lo), limit_upper=float(hi),
                                  armature=float(mj.dof_armature[mj.jnt_dofadr[j]]), effort_limit=1.0, label=bn + "_hinge")
    if hasattr(duck, "add_articulation"): duck.add_articulation([jid], label=bn)
    doors.append(bn)
ND, NQ = duck.joint_dof_count, duck.joint_coord_count

scene = newton.ModelBuilder()
scene.replicate(duck, N, spacing=(0.0, a.lane, 0.0))
scene.add_ground_plane()
model = scene.finalize(device=dev)
solver = newton.solvers.SolverMuJoCo(model, iterations=10, ls_iterations=50, integrator="euler", nconmax=160, njmax=600)
s0, s1, ctrl = model.state(), model.state(), model.control()
newton.eval_fk(model, model.joint_q, model.joint_qd, s0)
Q = lambda st: wp.to_torch(st.joint_q).view(N, NQ); QD = lambda st: wp.to_torch(st.joint_qd).view(N, ND)
torch.manual_seed(0)
Q(s0)[:, 7:nq_duck] += (torch.rand(N, 14, device=dev) * 2 - 1) * a.noise
newton.eval_fk(model, s0.joint_q, s0.joint_qd, s0)
tgt = wp.to_torch(ctrl.joint_target_q).view(N, -1)
tgt[:, TQ] = default
trunk = torch.arange(N, device=dev) * duck.body_count
origin = wp.to_torch(s0.body_q)[trunk][:, :2].clone(); origin[:, 0] = 0          # จุดเริ่มของแต่ละเลน
if os.environ.get("CAMDBG"): print("origin", origin.tolist())
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
q0 = Q(s0).clone()
physics()
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

# ---------------------------------------------------------------- กติกาเกม (tensor)
CP = torch.tensor([[c["x"], c["y"], c["z"]] for c in RULES["cps"]], device=dev)
WP = torch.tensor(RULES["waypoints"], device=dev)
BR = torch.tensor(RULES["bridge"], device=dev); LAVA = RULES["lava"]
cp = torch.zeros(N, dtype=torch.long, device=dev); wpi = torch.zeros(N, dtype=torch.long, device=dev)
tilt_t = torch.full((N,), -1.0, device=dev); falls = torch.zeros(N, dtype=torch.long, device=dev); lava_n = torch.zeros_like(falls)
finish = torch.full((N,), float("nan"), device=dev); cone_hits = torch.zeros_like(falls)
events = []

def seg_dist(p, A, B):
    d = B - A; t = ((p - A) @ d / (d @ d)).clamp(0, 1); return (p - (A + t[:, None] * d)).norm(dim=1)
def in_lava(p):
    inside = (p[:, 0] > LAVA[0]) & (p[:, 0] < LAVA[1]) & (p[:, 1] > LAVA[2]) & (p[:, 1] < LAVA[3])
    dmin = torch.stack([seg_dist(p, BR[i], BR[i + 1]) for i in range(len(BR) - 1)]).min(0).values
    return inside & (dmin > RULES["bridge_half"])

def respawn(mask, t, why):
    idx = mask.nonzero().flatten()
    if len(idx) == 0: return
    c = CP[cp[idx]]; nx = CP[(cp[idx] + 1).clamp(max=len(CP) - 1)]
    h = torch.atan2(nx[:, 1] - c[:, 1], nx[:, 0] - c[:, 0])
    q = Q(s0); q[idx, 0] = c[:, 0] + origin[idx, 0]; q[idx, 1] = c[:, 1] + origin[idx, 1]; q[idx, 2] = c[:, 2] + 0.125
    q[idx, 3] = 0; q[idx, 4] = 0; q[idx, 5] = torch.sin(h / 2); q[idx, 6] = torch.cos(h / 2)
    q[idx, 7:nq_duck] = default; QD(s0)[idx, :nd_duck] = 0; last[idx] = 0; tilt_t[idx] = -1
    newton.eval_fk(model, s0.joint_q, s0.joint_qd, s0)
    for i in idx.tolist():
        wpi[i] = int(((WP[:, 0] > CP[cp[i], 0] + 0.05).nonzero()[0]).item())
        events.append((round(t, 2), i, f"{why} → {RULES['cps'][cp[i]]['name']}"))

def game(t, bq):
    global cmd
    p = bq[:, :2] - origin; z = bq[:, 2]
    x, y, zq, w = bq[:, 3], bq[:, 4], bq[:, 5], bq[:, 6]
    up = 1 - 2 * (x * x + y * y)
    run = torch.isnan(finish)
    nxt = (cp + 1).clamp(max=len(CP) - 1)
    hit = run & (p[:, 0] >= CP[nxt, 0]) & ((p[:, 1] - CP[nxt, 1]).abs() < 0.3) & (z > CP[nxt, 2] + 0.06)
    for i in hit.nonzero().flatten().tolist():
        cp[i] += 1; events.append((round(t, 2), i, f"ผ่าน {RULES['cps'][cp[i]]['name']}"))
        if cp[i] == len(CP) - 1: finish[i] = t
    run = torch.isnan(finish)
    lv = run & in_lava(p); lava_n[lv] += 1; respawn(lv, t, "ตกลาวา")
    tilted = run & (up < 0.55)
    tilt_t[tilted & (tilt_t < 0)] = t; tilt_t[~tilted] = -1
    fl = tilted & (tilt_t >= 0) & (t - tilt_t > 0.5); falls[fl] += 1; respawn(fl, t, "ล้ม")
    # autopilot
    while True:
        wv = WP[wpi]; adv = run & (wpi < len(WP) - 1) & (((wv - p).norm(dim=1) < 0.1) | (wv[:, 0] < p[:, 0] + 0.02))
        if not adv.any(): break
        wpi[adv] += 1
    tv = WP[wpi] - p; yaw = torch.atan2(2 * (w * zq + x * y), 1 - 2 * (y * y + zq * zq))
    herr = torch.atan2(torch.sin(torch.atan2(tv[:, 1], tv[:, 0]) - yaw), torch.cos(torch.atan2(tv[:, 1], tv[:, 0]) - yaw))
    slow = torch.zeros(N, dtype=torch.bool, device=dev)
    for lo, hi in RULES["slow"]: slow |= (p[:, 0] >= lo) & (p[:, 0] <= hi)
    climb = (p[:, 0] >= RULES["stairs"][0] - 0.3) & (p[:, 0] <= RULES["stairs"][1])          # ตีนบันได → ยอด
    vset = torch.where(slow, a.vslow, a.vx)
    if a.vstairs is not None: vset = torch.where(climb, a.vstairs, vset)
    v = vset * torch.cos(herr).clamp(min=0) * (herr.abs() < 1.0)
    mountain = (p[:, 0] >= RULES["stairs"][0] - 0.3) & (p[:, 0] <= RULES["ramp_end"])       # ตีนบันได → ปลายทางลาด
    active[:] = torch.where(mountain, alt_idx, base_idx)
    wz = (2.5 * herr).clamp(-1, 1); wz = torch.where(herr.abs() > 0.08, torch.sign(herr) * torch.maximum(wz.abs(), torch.tensor(a.wzmin, device=dev)), wz)
    cmd[:, 0] = torch.where(run, v, 0.0); cmd[:, 2] = torch.where(run, wz, 0.0)

# ---------------------------------------------------------------- viewer
viewer = None
if a.video:
    import newton.viewer
    from PIL import Image
    W, H = map(int, a.res.split("x"))
    viewer = newton.viewer.ViewerGL(width=W, height=H, headless=True); viewer.set_model(model)
    viewer.set_world_offsets((0.0, 0.0, 0.0))                      # ไม่ให้ viewer เลื่อน world เพิ่ม — เลนอยู่ตรงตำแหน่งจริงในฟิสิกส์
    os.makedirs(a.video, exist_ok=True)
    mid_y = float(origin[:, 1].mean())
    def cam(bq):
        if a.cam == "overview":
            viewer.set_camera(wp.vec3(-1.2, mid_y - N * a.lane * 0.55 - 1.0, 2.6), -32.0, 52.0)
        elif a.cam.startswith("follow"):
            i = int(a.cam.split(":")[1]); fx, fy, fz = (float(v) for v in bq[i, :3])
            viewer.set_camera(wp.vec3(fx - 0.55, fy - 0.75, fz + 0.32), -20.0, 55.0)
            if os.environ.get("CAMDBG"): print("cam", fx, fy, fz, viewer.camera.pos, viewer.camera.yaw, viewer.camera.pitch)
        else:
            cx, cy, cz, cp_, cy_ = map(float, a.cam.split(",")); viewer.set_camera(wp.vec3(cx, cy, cz), cp_, cy_)

steps = int(a.secs * 50); torch.cuda.synchronize(); t0 = time.time(); nf = 0
with torch.no_grad():
    for k in range(steps):
        t = k * 0.02
        obs, bq = obs_now(k)
        game(t, bq)
        if not torch.isnan(finish).any() and t > float(finish.max()) + 2: break
        obs[:, -13:] = cmd
        act = policy(obs); last = act
        tgt[:, TQ] = default + act
        wp.capture_launch(graph)
        if viewer is not None and k % a.video_every == 0:
            cam(wp.to_torch(s0.body_q)[trunk])
            viewer.begin_frame(t); viewer.log_state(s0); viewer.end_frame()
            Image.fromarray(viewer.get_frame().numpy()).save(f"{a.video}/f_{nf:04d}.png"); nf += 1
torch.cuda.synchronize(); wall = time.time() - t0

endp = (wp.to_torch(s0.body_q)[trunk][:, :2] - origin).cpu()
res = dict(level=a.level, H=RULES["H"], N=N, sim_s=round(t, 1), wall_s=round(wall, 1), doors=doors, static_shapes=nstat, lanes=[])
for i in range(N):
    res["lanes"].append(dict(policy=POL[i // a.per], reached=RULES["cps"][int(cp[i])]["name"], cps=int(cp[i]),
                             finish=None if math.isnan(float(finish[i])) else round(float(finish[i]), 1), falls=int(falls[i]), lava=int(lava_n[i]),
                             end_x=round(float(endp[i, 0]), 2), end_y=round(float(endp[i, 1]), 2)))
summ = {}
for name in POL:
    L = [l for l in res["lanes"] if l["policy"] == name]
    summ[name] = dict(finished=sum(l["finish"] is not None for l in L), n=len(L), best=min([l["finish"] for l in L if l["finish"]] or [None], key=lambda v: v or 1e9),
                      falls_mean=round(sum(l["falls"] for l in L) / len(L), 1), cps=[l["cps"] for l in L])
res["summary"] = summ; res["events"] = events
print(json.dumps({k: v for k, v in res.items() if k not in ("events", "lanes")}, ensure_ascii=False))
if a.out: json.dump(res, open(a.out, "w"), ensure_ascii=False, indent=1)
