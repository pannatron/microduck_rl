"""กดปุ่มตามตารางเวลา: KEYS="2:k 5:y 9:y" """
import os
plan = sorted((float(t), k) for t, k in (x.split(":") for x in os.environ.get("KEYS", "").split()))
def control(t, pol, m, d):
    out = []
    while plan and plan[0][0] <= t: out.append(plan.pop(0)[1])
    return out

def report(m, d):
    import numpy as np
    q = d.qpos[3:7]; up = 1 - 2 * (q[1] ** 2 + q[2] ** 2)          # cos(tilt) ของลำตัว
    msg = f"END t={d.time:.1f}s trunk=({d.qpos[0]:+.3f},{d.qpos[1]:+.3f}) z={d.qpos[2]*1000:.0f}mm upright={up:.2f}"
    import mujoco
    j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_freejoint")
    if j < 0:
        for k in range(m.njnt):
            if m.jnt_type[k] == 0 and k > 0: j = k
    if j > 0:
        a = m.jnt_qposadr[j]; msg += f" ball=({d.qpos[a]:+.3f},{d.qpos[a+1]:+.3f})"
    print(msg)
