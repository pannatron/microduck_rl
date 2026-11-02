"""สัปดาห์ 9 · System ID บน test bench XL330 (ซิมล้วน — ใช้ BAM m6 แทน “มอเตอร์จริง”)

1. step response ของ BAM (ตัวที่ Pollen เทรน) ที่แรงดัน/น้ำหนักต่าง ๆ
2. ฟิต PD ธรรมดา (kp, kd, torque limit) ให้ตรงกับ BAM ด้วย least squares
3. เทียบกับค่า PD ที่เราใช้เทรนบน Newton (kp 0.55, kd 0.053, ±0.96 Nm)

พอมีมอเตอร์จริง: แทนข้อ 1 ด้วยไฟล์ที่ testbench_sim2real.py --mode real บันทึก แล้วรันข้อ 2 เหมือนเดิม
usage: python playground/sysid_testbench.py <out.json>
"""
import importlib.util, json, sys
import numpy as np, mujoco
from scipy.optimize import least_squares

SCENE = "src/mjlab_microduck/robot/xl330_test_bench/scene.xml"
spec = importlib.util.spec_from_file_location("ip", "scripts/infer_policy.py"); ip = importlib.util.module_from_spec(spec); spec.loader.exec_module(ip)
DT, T = 0.005, 2.0
STEPS = [(0.0, 1.0), (1.0, -0.5)]            # (เวลาเริ่ม s, มุมเป้าหมาย rad): ก้าว 57° แล้วถอยไป −29°


def target_at(t):
    return [a for t0, a in STEPS if t >= t0][-1]


def set_payload(m, mass):
    b = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "arm")
    s = mass / m.body_mass[b]; m.body_mass[b] = mass; m.body_inertia[b] *= s


def run_bam(vin=7.4, mass=0.12, drop=0.1):
    bm = ip.load_bam_model(200.0, vin, None)
    m, d, ctrl, _ = ip.load_mujoco_with_bam(SCENE, bm, DT, drop, 6.0)
    set_payload(m, mass); ctrl.reset(d.qpos)
    q = []
    for k in range(int(T / DT)):
        ctrl.q_target[:] = target_at(k * DT); ctrl.update(); mujoco.mj_step(m, d); q.append(d.qpos[0])
    return np.array(q)


def run_pd(kp, kd, flim, mass=0.12, armature=0.002, friction=0.0):
    m = mujoco.MjModel.from_xml_path(SCENE); m.opt.timestep = DT; set_payload(m, mass)
    m.actuator_gainprm[0, 0] = kp; m.actuator_biasprm[0, 1] = -kp; m.actuator_biasprm[0, 2] = 0.0
    m.actuator_forcerange[0] = (-flim, flim); m.dof_damping[0] = kd; m.dof_armature[0] = armature; m.dof_frictionloss[0] = friction
    d = mujoco.MjData(m); q = []
    for k in range(int(T / DT)):
        d.ctrl[0] = target_at(k * DT); mujoco.mj_step(m, d); q.append(d.qpos[0])
    return np.array(q)


def metrics(q):
    t = np.arange(len(q)) * DT; seg = q[: int(1.0 / DT)]
    rise = t[np.argmax(seg >= 0.9)] if (seg >= 0.9).any() else None
    return {"rise_90_ms": None if rise is None else round(rise * 1000), "overshoot_deg": round(float(np.degrees(max(seg.max() - 1.0, 0))), 1),
            "final_err_deg": round(float(np.degrees(abs(seg[-1] - 1.0))), 2)}


out = {"bam": {}, "fit": {}, "pd_ref": {}}
ref = run_bam()
out["bam"]["nominal"] = metrics(ref)
for vin in (6.5, 8.2):
    out["bam"][f"vin_{vin}"] = metrics(run_bam(vin=vin))
for mass in (0.05, 0.25):
    out["bam"][f"mass_{mass}"] = metrics(run_bam(mass=mass))

# PD ที่เราใช้เทรนบน Newton และ PD ของ MJCF เป็ด (kv = 0, damping 0.053 จาก joint)
for name, (kp, kd, fl) in {"newton_isaaclab": (0.55, 0.053 + 0.053, 0.96), "mjcf_duck": (0.55, 0.053, 0.96), "mjcf_testbench": (0.386, 0.041, 0.67)}.items():
    q = run_pd(kp, kd, fl); out["pd_ref"][name] = {**metrics(q), "rmse_vs_bam_deg": round(float(np.degrees(np.sqrt(np.mean((q - ref) ** 2)))), 2)}

res = least_squares(lambda x: run_pd(*x) - ref, x0=[0.55, 0.05, 0.96], bounds=([0.05, 0.0, 0.1], [5.0, 1.0, 3.0]), diff_step=1e-3)
qf = run_pd(*res.x)
out["fit"] = {"kp": round(float(res.x[0]), 3), "kd": round(float(res.x[1]), 4), "torque_limit": round(float(res.x[2]), 3),
              "rmse_deg": round(float(np.degrees(np.sqrt(np.mean((qf - ref) ** 2)))), 2), **metrics(qf)}
np.savez(sys.argv[1].replace(".json", ".npz"), bam=ref, fit=qf, newton=run_pd(0.55, 0.106, 0.96), duck=run_pd(0.55, 0.053, 0.96),
         bam_v65=run_bam(vin=6.5), bam_m25=run_bam(mass=0.25), t=np.arange(len(ref)) * DT)
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
