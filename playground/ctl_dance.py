"""ท่าเต้น: keyframe ของ head_pose + body_pose + twist → ใส่ในช่อง command 13 มิติ
KF: (เวลา s, head_yaw, head_pitch, body_roll, body_pitch, vx, wz)  — มุมเป็น rad
SCALE คูณมุม body ทั้งหมด (ลองเกินช่วงที่เทรนได้)"""
import os, math, numpy as np
SCALE = float(os.environ.get("SCALE", "1.0"))
D = math.radians
KF = [  # t   h_yaw     h_pitch   b_roll   b_pitch   vx    wz
    (0.0,  0,        0,        0,       0,        0,    0),
    (1.5,  0,        0,        0,       0,        0,    0),
    (2.5,  D(45),    0,        0,       0,        0,    0),    # หันซ้าย
    (3.5,  D(-45),   0,        0,       0,        0,    0),    # หันขวา
    (4.5,  0,        D(-25),   0,       0,        0,    0),    # ก้มหัว
    (5.5,  0,        D(20),    0,       0,        0,    0),    # เงยหัว
    (6.5,  0,        0,        D(8),    0,        0,    0),    # เอียงตัวซ้าย
    (7.5,  0,        0,        D(-8),   0,        0,    0),    # เอียงตัวขวา
    (8.5,  0,        0,        0,       D(8),     0,    0),    # โค้ง
    (9.5,  0,        0,        0,       D(-6),    0,    0),
    (10.5, 0,        0,        0,       0,        0,    0),
    (11.0, D(30),    0,        0,       0,        0,    1.0),  # หมุนตัวไปพร้อมหันหัว
    (14.0, D(30),    0,        0,       0,        0,    1.0),
    (14.5, 0,        0,        0,       0,        0,    0),
    (17.0, 0,        0,        0,       0,        0,    0),
]
T = np.array([k[0] for k in KF]); V = np.array([k[1:] for k in KF])
def at(t):
    i = int(np.clip(np.searchsorted(T, t) - 1, 0, len(T) - 2)); u = np.clip((t - T[i]) / (T[i + 1] - T[i]), 0, 1)
    u = 0.5 - 0.5 * math.cos(math.pi * u)          # smoothstep แบบ cosine
    return V[i] * (1 - u) + V[i + 1] * u
log = []
def rp(d):
    w, x, y, z = d.qpos[3:7]
    return math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y)), math.asin(np.clip(2 * (w * y - z * x), -1, 1))
def control(t, pol, m, d):
    hy, hp, br, bp, vx, wz = at(t)
    pol.head_offset[:] = [0, hp, hy, 0]
    pol.body_cmd[:] = [0, 0, 0, br * SCALE, bp * SCALE, 0]   # [x, y, z, roll, pitch, yaw]
    pol.vel_cmd = np.array([vx, 0, wz], dtype=np.float32); pol._update_policy_session(); pol._update_command()
    j = pol.joint_qpos_indices; q = d.qpos[j] - pol.default_pose
    r, p = rp(d); log.append((t, hy, hp, br * SCALE, bp * SCALE, q[7], q[6], r, p, d.qvel[5]))
def report(m, d):
    L = np.array(log); L = L[L[:, 0] > 1.5]
    w, x, y, z = d.qpos[3:7]
    # หมายเหตุ: ท่ายืนปกติมี roll/pitch ไม่เป็นศูนย์ จึงเทียบกับค่าเฉลี่ยช่วงแรก
    base = np.array(log)[50:75].mean(0)
    def err(c, a, b0=0): return np.degrees(np.sqrt(np.mean((L[:, c] - (L[:, a] - b0)) ** 2)))
    print(f"END upright={1 - 2 * (x * x + y * y):.2f} fell={1 - 2 * (x * x + y * y) < 0.8} "
          f"rms_err head_yaw={err(1, 5):.1f}deg head_pitch={err(2, 6):.1f}deg body_roll={err(3, 7, base[7]):.1f}deg body_pitch={err(4, 8, base[8]):.1f}deg "
          f"peak_roll={np.degrees(np.max(np.abs(L[:, 7] - base[7]))):.1f}deg")
    np.save(os.environ.get("DLOG", "/tmp/dance.npy"), np.array(log))
