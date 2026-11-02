"""MuJoCo CPU แบบ infer_policy --no-bam แต่เขียนเองสั้น ๆ: บันทึก obs/action 50 step แรก (ไว้เทียบกับ Newton)"""
import sys, numpy as np, mujoco, onnxruntime as ort
pol, vx, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
m = mujoco.MjModel.from_xml_path("src/mjlab_microduck/robot/microduck/scene.xml"); m.opt.timestep = 0.005; d = mujoco.MjData(m)
P = np.load("newton_port/walk_2000.npz"); dp = P["default_pose"]
d.qpos[:7] = [0, 0, 0.125, 1, 0, 0, 0]; d.qpos[7:] = dp; d.ctrl[:] = dp; mujoco.mj_forward(m, d)
S = ort.InferenceSession(pol); gy = m.sensor_adr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SENSOR, "imu_ang_vel")]
tb = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "trunk_base")
last = np.zeros(14, np.float32); cmd = np.zeros(13, np.float32); cmd[0] = vx; D = []
def rinv(q, v):
    w, x, y, z = q; u = -np.array([x, y, z]); t = 2 * np.cross(u, v); return v + w * t + np.cross(u, t)
for k in range(1000):
    o = np.concatenate([d.sensordata[gy:gy + 3], rinv(d.xquat[tb], np.array([0, 0, -1.])), d.qpos[7:] - dp, d.qvel[6:], last, cmd]).astype(np.float32)
    a = S.run(None, {S.get_inputs()[0].name: o[None]})[0][0]; last = a
    if k < 50: D.append((o, a))
    d.ctrl[:] = dp + a
    for _ in range(4): mujoco.mj_step(m, d)
    if k == 499: x0 = d.qpos[:2].copy(); t0 = d.time
print("fwd(avg 10s) %.3f" % (np.linalg.norm(d.qpos[:2] - x0) / (d.time - t0)))
np.savez(out, obs=np.array([x[0] for x in D]), act=np.array([x[1] for x in D]))
