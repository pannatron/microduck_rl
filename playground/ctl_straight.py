"""เดินตรงไปข้างหน้าด้วย P-controller บนมุม yaw (แก้อาการเดินวน)
VX = ความเร็วที่สั่ง, KP = gain ของ yaw (0 = ไม่แก้)"""
import os, math
X0 = float(os.environ.get("X0", "0"))   # เลื่อนจุดเริ่ม (ใช้ทำหลาย trial)
_moved = [False]
VX = float(os.environ.get("VX", "0.3")); KP = float(os.environ.get("KP", "2.0")); T0 = 1.0
def yaw_of(d):
    w, x, y, z = d.qpos[3:7]; return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
def set_cmd(pol, vx, vy, wz):          # เหมือน pol.set_vel_cmd แต่ไม่ print ทุก step
    import numpy as np
    pol.vel_cmd = np.array([vx, vy, wz], dtype=np.float32); pol._update_policy_session(); pol._update_command()
def control(t, pol, m, d):
    if not _moved[0]:
        d.qpos[0] += X0; _moved[0] = True
    if t < T0: return []
    wz = max(-1.0, min(1.0, -KP * yaw_of(d) - 3.0 * KP * d.qpos[1]))   # หันกลับหาแกน x (y→0)
    set_cmd(pol, VX, 0.0, wz); return []
def report(m, d):
    w, x, y, z = d.qpos[3:7]; up = 1 - 2 * (x * x + y * y)
    print(f"END x={d.qpos[0]:+.3f} y={d.qpos[1]:+.3f} z={d.qpos[2]*1000:.0f}mm upright={up:.2f} yaw={math.degrees(yaw_of(d)):+.0f}deg")
