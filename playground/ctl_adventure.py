"""Duck Adventure — กติกาเกม + autopilot  (ใช้คู่กับ sim_play.py + scene จาก make_adventure.py)

ADV=src/.../scene_adventure.json   ไฟล์กติกาที่ make_adventure.py เขียนคู่กับ scene
AUTO=1                             ให้ autopilot เดินตาม waypoint (ค่าเริ่มต้น) · AUTO=0 = คนบังคับเองด้วยลูกศร (sim_play --live)
VX=0.4 VSLOW=0.3 WZMIN=0.5         ความเร็วปกติ / ในโซนยาก (m/s) / คำสั่งเลี้ยวขั้นต่ำ (rad/s — policy มี "โซนตาย" ที่คำสั่งเลี้ยวเล็ก ๆ ไม่ทำอะไรเลย)

กติกา: เดินข้ามเส้นวงเขียว (ตามลำดับ) = checkpoint · ล้ม (เอียงเกิน ~55° นาน 0.5 s) หรือตกลาวา = เกิดใหม่ที่ checkpoint ล่าสุด
       ชนกรวย = +2 s · คะแนน = เวลาในซิม + โทษ  · เกิน 180 s = หมดเวลา
"""
import os, math, json, numpy as np, mujoco
R = json.load(open(os.environ.get("ADV", "src/mjlab_microduck/robot/microduck/scene_adventure.json")))
AUTO = os.environ.get("AUTO", "1") == "1"
VX, VSLOW = float(os.environ.get("VX", "0.4")), float(os.environ.get("VSLOW", "0.3"))
WZMIN = float(os.environ.get("WZMIN", "0.5"))
TIME_LIMIT = float(os.environ.get("TIME_LIMIT", "180"))
CPS, WP = R["cps"], [np.array(w) for w in R["waypoints"]]
S = None                                    # sim_play ใส่ state (viewer ฯลฯ) ให้
st = dict(cp=0, wp=0, events=[], respawns=0, lava=0, falls=0, cone_hits=0, penalty=0.0, tilt_t=None, done=False, cone_touch=set(), last_hud=-1, init=False, trace=[])


def yaw_of(d):
    w, x, y, z = d.qpos[3:7]; return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
def upright(d): x, y = d.qpos[4:6]; return 1 - 2 * (x * x + y * y)
def set_cmd(pol, vx, vy, wz):
    pol.vel_cmd = np.array([vx, vy, wz], dtype=np.float32); pol._update_policy_session(); pol._update_command()


def seg_dist(p, a, b):
    a, b = np.array(a), np.array(b); t = np.clip(np.dot(p - a, b - a) / np.dot(b - a, b - a), 0, 1); return np.linalg.norm(p - (a + t * (b - a)))
def in_lava(p):
    x0, x1, y0, y1 = R["lava"]
    if not (x0 < p[0] < x1 and y0 < p[1] < y1): return False
    return min(seg_dist(p, a, b) for a, b in zip(R["bridge"], R["bridge"][1:])) > R["bridge_half"]


def log(t, msg):
    st["events"].append((round(t, 2), msg)); print(f"[{t:6.1f}s] {msg}", flush=True)


def respawn(t, pol, m, d, why):
    where = f"(x={d.qpos[0]:.2f}, y={d.qpos[1]:+.2f})"
    c = CPS[st["cp"]]; st["respawns"] += 1; st[why] += 1
    key = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "STAND")
    d.qpos[7:21] = m.key_qpos[key][7:21]; d.qvel[:] = 0
    nxt = CPS[min(st["cp"] + 1, len(CPS) - 1)]; h = math.atan2(nxt["y"] - c["y"], nxt["x"] - c["x"])
    d.qpos[0:7] = [c["x"], c["y"], c["z"] + 0.12, math.cos(h / 2), 0, 0, math.sin(h / 2)]
    pol.last_action[:] = 0; st["tilt_t"] = None
    # autopilot: ย้อน waypoint กลับมาที่อันแรกที่อยู่หลัง checkpoint นี้
    st["wp"] = next(i for i, w in enumerate(WP) if w[0] > c["x"] + 0.05)
    mujoco.mj_forward(m, d); log(t, f"{'ตกลาวา' if why == 'lava' else 'ล้ม'} ที่ {where} → เกิดใหม่ที่ {c['name']}")


def hud(t):
    if int(t) == st["last_hud"]: return
    st["last_hud"] = int(t)
    txt = f"{CPS[st['cp']]['name']}  เวลา {t:5.1f}s  โทษ +{st['penalty']:.0f}s  เกิดใหม่ {st['respawns']}"
    v = (S or {}).get("viewer")
    if v is not None and hasattr(v, "set_texts"):
        try: v.set_texts((mujoco.mjtFontScale.mjFONTSCALE_150, mujoco.mjtGridPos.mjGRID_TOPLEFT, "Duck Adventure", txt))
        except Exception: pass
    elif not AUTO: print("\r" + txt, end="\r\n", flush=True)


def control(t, pol, m, d):
    if st["done"]: return []
    if not st["init"]:
        st["init"] = True; st["cone_ids"] = {mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, f"cone{i}") for i in range(len(R["cones"]))}
        log(t, f"เริ่ม! ด่าน H={R['H']*1000:.0f} mm  {'autopilot' if AUTO else 'บังคับเอง: ↑↓←→'}")
    p = d.qpos[:2].copy(); hud(t)
    if not st["trace"] or t - st["trace"][-1][0] >= 1.0: st["trace"].append((round(t, 1), round(float(p[0]), 3), round(float(p[1]), 3), round(float(d.qpos[2]), 3)))
    # --- checkpoint ถัดไป (ต้องผ่านตามลำดับ)
    nxt = CPS[st["cp"] + 1]
    if p[0] >= nxt["x"] and abs(p[1] - nxt["y"]) < 0.3 and d.qpos[2] > nxt["z"] + 0.06:      # ข้ามเส้น checkpoint (กว้าง ±30 ซม.)
        st["cp"] += 1; log(t, f"ผ่าน {nxt['name']} ✓")
        if nxt["name"] == "FINISH":
            st["done"] = True; st["finish"] = t; set_cmd(pol, 0, 0, 0)
            log(t, f"เข้าเส้นชัย! คะแนน {t + st['penalty']:.1f} s (เวลา {t:.1f} + โทษ {st['penalty']:.0f})"); return []
    # --- ชนกรวย
    for i in range(d.ncon):
        c = d.contact[i]
        for gid in (c.geom1, c.geom2):
            if gid in st["cone_ids"] and gid not in st["cone_touch"]:
                st["cone_touch"].add(gid); st["cone_hits"] += 1; st["penalty"] += 2; log(t, "ชนกรวย +2 s")
    # --- ลาวา / ล้ม
    if in_lava(p): respawn(t, pol, m, d, "lava"); return []
    if upright(d) < 0.55:
        st["tilt_t"] = st["tilt_t"] or t
        if t - st["tilt_t"] > 0.5: respawn(t, pol, m, d, "falls"); return []
    else: st["tilt_t"] = None
    if t > TIME_LIMIT: st["done"] = True; log(t, "หมดเวลา"); return []
    # --- autopilot: เล็งหัวไปที่ waypoint ถัดไป
    if AUTO:
        while st["wp"] < len(WP) - 1 and (np.linalg.norm(WP[st["wp"]] - p) < 0.1 or WP[st["wp"]][0] < p[0] + 0.02):   # ถึงแล้ว หรือเลยแนว x ไปแล้ว (กันวนรอบ waypoint)
            st["wp"] += 1
        tgt = WP[st["wp"]]; herr = wrap(math.atan2(*(tgt - p)[::-1]) - yaw_of(d))
        slow = any(a <= p[0] <= b for a, b in R["slow"])
        v = (VSLOW if slow else VX) * max(0.0, math.cos(herr)) if abs(herr) < 1.0 else 0.0
        wz = float(np.clip(2.5 * herr, -1.0, 1.0))
        if abs(herr) > 0.08: wz = math.copysign(max(abs(wz), WZMIN), herr)
        set_cmd(pol, v, 0.0, wz)
    return []


def report(m, d):
    res = dict(H=R["H"], reached=CPS[st["cp"]]["name"], cps=st["cp"], finish=st.get("finish"), penalty=st["penalty"],
               respawns=st["respawns"], lava=st["lava"], falls=st["falls"], cone_hits=st["cone_hits"], events=st["events"], trace=st["trace"])
    print("ADVENTURE " + json.dumps({k: v for k, v in res.items() if k != "trace"}, ensure_ascii=False))
    out = os.environ.get("ADV_OUT")
    if out: json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
