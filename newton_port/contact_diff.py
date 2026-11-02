"""รัน policy เดียวกันบน 2 MJCF (ต้นฉบับ vs ที่ Newton แปลง) แล้วดูรายการ contact ทีละ step"""
import sys, numpy as np, mujoco, onnxruntime as ort
P = np.load("newton_port/walk_2000.npz"); dp = P["default_pose"]
S = ort.InferenceSession("exports/walk_2000.onnx")
def run(xml, steps=6):
    m = mujoco.MjModel.from_xml_path(xml); m.opt.timestep = 0.005; m.opt.integrator = 0; m.opt.iterations = 100; d = mujoco.MjData(m)
    d.qpos[:7] = [0, 0, 0.125, 1, 0, 0, 0]; d.qpos[7:21] = dp; d.ctrl[:] = dp; mujoco.mj_forward(m, d)
    last = np.zeros(14, np.float32); cmd = np.zeros(13, np.float32); cmd[0] = 0.3; gyro = np.zeros(3); quat = np.array([1., 0, 0, 0]); out = []
    def rinv(q, v):
        w, x, y, z = q; u = -np.array([x, y, z]); t = 2 * np.cross(u, v); return v + w * t + np.cross(u, t)
    for k in range(steps):
        o = np.concatenate([gyro, rinv(quat, np.array([0, 0, -1.])), d.qpos[7:21] - dp, d.qvel[6:20], last, cmd]).astype(np.float32)
        a = S.run(None, {S.get_inputs()[0].name: o[None]})[0][0]; last = a; d.ctrl[:] = dp + a
        for i in range(4):
            if i == 3: gyro = d.qvel[3:6].copy(); quat = d.qpos[3:7].copy()
            mujoco.mj_step(m, d)
            pairs = sorted((mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[c.geom1]) or "world",
                            mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[c.geom2]) or "world") for c in d.contact[:d.ncon])
            out.append((k, i, d.ncon, [(p[0].split("/")[-1], p[1].split("/")[-1]) for p in pairs], d.qvel[6:20].copy()))
    return out
A = run("src/mjlab_microduck/robot/microduck/scene.xml"); B = run("newton_port/newton_export.xml")
for x, y in zip(A, B):
    dq = np.abs(x[4] - y[4]).max()
    print(f"step {x[0]}.{x[1]} ncon {x[2]} vs {y[2]}  |dqd|={dq:.4f}", "" if x[3] == y[3] else f"\n   A {x[3]}\n   B {y[3]}")
