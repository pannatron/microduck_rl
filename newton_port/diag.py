"""หาว่า solver ที่ไม่ใช่ MuJoCo ระเบิดตอนไหน: เป็ดยืนเฉย ๆ (ไม่มี policy)
usage: diag.py <featherstone|semi|xpbd> <selfcollide 0/1> <dt>"""
import sys, numpy as np, warp as wp, newton
XML = "/home/ubuntu/repos/microduck_rl/src/mjlab_microduck/robot/microduck/robot_groundcontact.xml"
solver_name, selfcol, dt = sys.argv[1], sys.argv[2] == "1", float(sys.argv[3])
P = np.load("/home/ubuntu/repos/microduck_rl/newton_port/walk_2000.npz")
b = newton.ModelBuilder()
b.add_mjcf(XML, floating=True, parse_visuals=False, enable_self_collisions=selfcol)
for i in range(6, b.joint_dof_count):
    b.joint_effort_limit[i] = 0.96
b.joint_q[0:7] = [0, 0, 0.125, 0, 0, 0, 1]
b.joint_q[7:] = P["default_pose"].tolist()
b.joint_target_q[-14:] = P["default_pose"].tolist()
print("shapes", b.shape_count, "mass min %.4g" % min(b.body_mass),
      "inertia min diag %.3g" % min(min(np.diag(np.array(I).reshape(3, 3))) for I in b.body_inertia))
b.add_ground_plane()
import os
KE, KD = float(os.environ.get('KE', 2500)), float(os.environ.get('KD', 100))
for i in range(b.shape_count):
    b.shape_material_ke[i] = KE; b.shape_material_kd[i] = KD
m = b.finalize()
S = {"featherstone": newton.solvers.SolverFeatherstone, "semi": newton.solvers.SolverSemiImplicit,
     "xpbd": newton.solvers.SolverXPBD}[solver_name](m)
s0, s1, c = m.state(), m.state(), m.control()
newton.eval_fk(m, m.joint_q, m.joint_qd, s0)
for k in range(int(2.0 / dt)):
    s0.clear_forces()
    S.step(s0, s1, c, m.collide(s0), dt)
    s0, s1 = s1, s0
    q = s0.joint_q.numpy()
    if not np.isfinite(q).all():
        print("NaN at step", k, "t=%.4f" % (k * dt))
        break
    if k % int(0.25 / dt) == 0:
        print("t=%.2f z=%.4f maxqd=%.1f" % (k * dt, q[2], np.abs(s0.joint_qd.numpy()).max()))
else:
    print("ok z=%.4f" % s0.joint_q.numpy()[2])
