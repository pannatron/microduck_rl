"""แปลง ONNX (normalizer + MLP ELU) → npz ให้ฝั่ง Newton รันด้วย torch ได้โดยไม่ต้องมี onnxruntime
และเก็บข้อมูล MJCF ที่ต้องใช้สร้าง obs (default pose, ตำแหน่ง/มุมของ IMU site)"""
import sys, onnx, numpy as np, mujoco
from onnx import numpy_helper
src, dst = sys.argv[1], sys.argv[2]
g = onnx.load(src).graph
W = {i.name: numpy_helper.to_array(i) for i in g.initializer}
ops = [n.op_type for n in g.node]
assert ops[:2] == ["Sub", "Div"] and set(ops[2:]) <= {"Gemm", "Elu"}, ops
gemms = [n for n in g.node if n.op_type == "Gemm"]
out = {"mean": W[g.node[0].input[1]], "std": W[g.node[1].input[1]]}
for k, n in enumerate(gemms):
    out[f"w{k}"] = W[n.input[1]]; out[f"b{k}"] = W[n.input[2]]
m = mujoco.MjModel.from_xml_path("src/mjlab_microduck/robot/microduck/scene.xml"); d = mujoco.MjData(m)
k = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "STAND")
out["default_pose"] = m.key_qpos[k][7:].astype(np.float32)
s = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")
out["imu_quat"] = m.site_quat[s].astype(np.float32)        # wxyz ใน frame ของ trunk_base
out["imu_body"] = np.array(m.site_bodyid[s])
print(dst, "layers", len(gemms), "imu body", mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.site_bodyid[s]), "quat", out["imu_quat"])
np.savez(dst, **out)
