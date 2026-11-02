"""ตารางคำสั่งสำหรับเป็ดล้อ: CMDS="0:0.6 3:0.2" = เวลา 0 s สั่ง 0.6, เวลา 3 s เปลี่ยนเป็น 0.2
บันทึกความเร็วไปข้างหน้า (เฉลี่ยทุก 1 s) ลง LOG"""
import os, math, json, numpy as np
plan = sorted((float(t), float(v)) for t, v in (x.split(":") for x in os.environ.get("CMDS", "0:0.4").split()))
cur = [None]; hist = []
FRIC = os.environ.get("WHEEL_FRIC")    # แรงเสียดทานลูกปืนล้อ (infer_policy ตั้ง 0.003, ตอนเทรนสูงสุด 0.0015)
_set = [False]
def control(t, pol, m, d):
    if FRIC is not None and not _set[0]:
        import mujoco
        for j in range(m.njnt):
            n = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j) or ""
            if n.startswith("passive_"): m.dof_frictionloss[m.jnt_dofadr[j]] = float(FRIC)
        _set[0] = True
    v = [c for tt, c in plan if tt <= t][-1]
    if v != cur[0]:
        pol.vel_cmd = np.array([v, 0, 0], dtype=np.float32); pol._update_policy_session(); pol._update_command(); cur[0] = v
    w, x, y, z = d.qpos[3:7]; yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    hist.append((t, d.qpos[0], d.qpos[1], yaw, v, d.qpos[2]))
    return []
def report(m, d):
    H = np.array(hist); out = []
    for s in range(int(H[-1, 0])):
        a = H[(H[:, 0] >= s) & (H[:, 0] < s + 1)]
        if len(a) > 2:
            dx, dy = a[-1, 1] - a[0, 1], a[-1, 2] - a[0, 2]; yaw = a[0, 3]
            out.append((s, round(float(a[0, 4]), 2), round(float((dx * math.cos(yaw) + dy * math.sin(yaw)) / (a[-1, 0] - a[0, 0])), 3), round(float(a[:, 5].min()) * 1000)))
    print("SPEEDS " + json.dumps(out))
