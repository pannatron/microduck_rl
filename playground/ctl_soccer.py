"""แอป: เดินไปหาลูกบอล → จัดท่าให้บอลอยู่หน้าเท้าซ้าย → กด K เตะเข้าประตู
state machine:  APPROACH → ALIGN → SETTLE → KICK → DONE"""
import os, math, numpy as np
BALL0 = [float(v) for v in os.environ.get("BALL", "0.8,0.4").split(",")]
GOAL = np.array([2.0, 0.0])
AIM = math.radians(float(os.environ.get("AIM", "0")))   # ชดเชยมุมเตะ (องศา, + = หันขวามากขึ้น)
VMIN = float(os.environ.get("VMIN", "0"))        # คำสั่งขั้นต่ำตอนจัดท่า (0 = ปิด)
TOL = float(os.environ.get("TOL", "0.03"))        # ระยะคลาดเคลื่อนที่ยอมให้ก่อนเตะ (ม.)
OFF = np.array([0.09, 0.042])                 # ตำแหน่งบอลที่ kick policy ถูกเทรนมา (เฟรมหุ่น: หน้า 9 ซม. ซ้าย 4.2 ซม.)
ALIGN_TIMEOUT = 12.0
st = {"s": "INIT", "t": 0.0, "log": [], "cross": None, "kick": None, "prev": None}

def yaw_of(d):
    w, x, y, z = d.qpos[3:7]; return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
def set_cmd(pol, vx, vy, wz):
    pol.vel_cmd = np.array([vx, vy, wz], dtype=np.float32); pol._update_policy_session(); pol._update_command()
def ball(pol, d): a = pol.ball_qpos_adr; return d.qpos[a:a + 2].copy()

def target_pose(b):
    """ยืนตรงไหน หันทางไหน เพื่อให้บอลอยู่ที่ OFF และแนวเตะชี้เข้าประตู"""
    h = math.atan2(*(GOAL - b)[::-1]) - AIM; R = np.array([[math.cos(h), -math.sin(h)], [math.sin(h), math.cos(h)]])
    return b - R @ OFF, h

def go(t, s):
    st["s"], st["t"] = s, t; print(f"[{t:5.1f}s] → {s}")

def control(t, pol, m, d):
    s = st["s"]; p = d.qpos[:2]; yaw = yaw_of(d)
    if s == "INIT":
        pol._place_ball = lambda name: None    # ปิดการ "วาร์ปบอล" ของสคริปต์เดิม — ต้องเดินไปเองจริง ๆ
        a = pol.ball_qpos_adr; d.qpos[a:a + 3] = [*BALL0, 0.035]; go(t, "APPROACH"); return []
    b = ball(pol, d); tp, th = target_pose(b)
    e_w = tp - p; e = np.array([[math.cos(yaw), math.sin(yaw)], [-math.sin(yaw), math.cos(yaw)]]) @ e_w   # error ในเฟรมหุ่น
    dist = np.linalg.norm(e_w); st["log"].append((t, *p, yaw, s, *b))
    if st["prev"] is not None and st["prev"][0] < GOAL[0] <= b[0] and st["cross"] is None: st["cross"] = b[1]   # y ตอนข้ามเส้นประตู
    st["prev"] = b
    if s == "APPROACH":                       # ไกล: หันหน้าเข้าหาเป้า แล้วเดินหน้า (วนอ้อมให้มาจากด้านหลังบอล)
        pre = tp - 0.12 * np.array([math.cos(th), math.sin(th)])
        e2 = pre - p; head = math.atan2(e2[1], e2[0]); herr = wrap(head - yaw)
        vx = 0.3 if abs(herr) < 0.5 else 0.0
        set_cmd(pol, vx, 0.0, float(np.clip(2.0 * herr, -1, 1)))
        if np.linalg.norm(e2) < 0.06: go(t, "ALIGN")
    elif s == "ALIGN":                        # ใกล้: ปรับละเอียดทั้ง x, y, yaw พร้อมกัน
        herr = wrap(th - yaw)
        vx = float(np.clip(2.5 * e[0], -0.3, 0.3)); vy = float(np.clip(2.5 * e[1], -0.2, 0.2))
        if VMIN > 0:                          # ดันให้พ้น "โซนตาย" ของ policy: ถ้ายังคลาดเกิน TOL/2 สั่งอย่างน้อย VMIN
            if abs(e[0]) > TOL / 2: vx = math.copysign(max(abs(vx), VMIN), e[0])
            if abs(e[1]) > TOL / 2: vy = math.copysign(max(abs(vy), VMIN * 0.7), e[1])
        set_cmd(pol, vx, vy, float(np.clip(2.0 * herr, -1, 1)))
        if dist < TOL * 0.66 and abs(herr) < 0.08: set_cmd(pol, 0, 0, 0); go(t, "SETTLE")
        elif t - st["t"] > ALIGN_TIMEOUT: set_cmd(pol, 0, 0, 0); go(t, "SETTLE")       # กันค้าง
    elif s == "SETTLE":                       # หยุดนิ่งให้ท่ายืนเข้าที่ก่อนเตะ
        if t - st["t"] > 1.0:
            if dist < TOL and abs(wrap(th - yaw)) < 0.12: go(t, "KICK"); st["kick"] = (b.copy(), yaw, math.atan2(*(GOAL - b)[::-1])); st["err"] = (e[0], e[1], wrap(th - yaw)); return ["k"]
            go(t, "ALIGN")
    elif s == "KICK":
        if t - st["t"] > 3.5: go(t, "DONE")
    return []

def report(m, d):
    import mujoco
    j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_freejoint"); a = m.jnt_qposadr[j] if j >= 0 else None
    if a is None:
        for k in range(1, m.njnt):
            if m.jnt_type[k] == 0: a = m.jnt_qposadr[k]
    b = d.qpos[a:a + 2]; w, x, y, z = d.qpos[3:7]; extra = ""
    if st["kick"] is not None:
        b0, yk, gdir = st["kick"]; dv = b - b0; moved = np.linalg.norm(dv)
        if moved > 0.05: extra = f" kick_dir_vs_body={math.degrees(wrap(math.atan2(dv[1], dv[0]) - yk)):+.0f}deg miss_vs_goal={math.degrees(wrap(math.atan2(dv[1], dv[0]) - gdir)):+.0f}deg dist={moved:.2f}m"
        else: extra = " kick_missed_ball"
        ex, ey, eh = st["err"]; extra += f" align_err=({ex*1000:+.0f},{ey*1000:+.0f})mm,{math.degrees(eh):+.0f}deg"
    goal = st["cross"] is not None and abs(st["cross"]) < 0.25
    print(f"END state={st['s']} GOAL={goal} cross_y={st['cross'] if st['cross'] is None else round(float(st['cross']), 2)}{extra} "
          f"upright={1 - 2 * (x * x + y * y):.2f}")
