"""นับ contact ที่เท้าเป็ดตอนยืน: MuJoCo CPU vs MuJoCo Warp (ตัวที่ mjlab ใช้เทรน) บนโมเดลเดียวกัน"""
import numpy as np, mujoco, mujoco_warp as mjw, warp as wp
m = mujoco.MjModel.from_xml_path("src/mjlab_microduck/robot/microduck/scene.xml"); m.opt.timestep = 0.005
d = mujoco.MjData(m); k = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "STAND"); mujoco.mj_resetDataKeyframe(m, d, k)
d.qpos[2] = 0.125
for _ in range(200): mujoco.mj_step(m, d)          # ยืนให้เท้าแตะพื้นก่อน (1 s)
mujoco.mj_forward(m, d)
print("CPU   ncon", d.ncon, "dist", np.round(d.contact.dist[:d.ncon], 4))
mm = mjw.put_model(m); dd = mjw.put_data(m, d, nconmax=64, njmax=256)
mjw.forward(mm, dd); wp.synchronize()
n = int(dd.nacon.numpy()[0]) if hasattr(dd, "nacon") else int(dd.ncon.numpy()[0])
dist = dd.contact.dist.numpy()[:n]
print("MJWarp ncon", n, "dist", np.round(dist, 4))
