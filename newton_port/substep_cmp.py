"""เทียบทีละ substep: Newton(SolverMuJoCo, CPU) vs MuJoCo native บน obs/action เดียวกัน (ใช้ action จาก native)"""
import numpy as np, newton, warp as wp, mujoco
XML = "/home/ubuntu/repos/microduck_rl/src/mjlab_microduck/robot/microduck/robot_groundcontact.xml"
P = np.load("/home/ubuntu/repos/microduck_rl/newton_port/walk_2000.npz"); dp = P["default_pose"]
ACT = np.load("/tmp/claude-1000/-home-ubuntu/d4506bc5-6836-41c4-83f6-b5ca0a7707b3/scratchpad/native.npz")["act"]
b = newton.ModelBuilder(); b.add_mjcf(XML, floating=True, parse_visuals=False, enable_self_collisions=False)
for i in range(6, b.joint_dof_count): b.joint_effort_limit[i] = 0.96
b.joint_q[0:7] = [0, 0, 0.125, 0, 0, 0, 1]; b.joint_q[7:] = dp.tolist(); b.joint_target_q[-14:] = dp.tolist()
b.add_ground_plane(); m = b.finalize()
sol = newton.solvers.SolverMuJoCo(m, iterations=100, ls_iterations=50, integrator="euler", use_mujoco_cpu=True)
s0, s1, c = m.state(), m.state(), m.control(); newton.eval_fk(m, m.joint_q, m.joint_qd, s0)
# native
M = mujoco.MjModel.from_xml_path("/home/ubuntu/repos/microduck_rl/src/mjlab_microduck/robot/microduck/scene.xml"); M.opt.timestep = 0.005
D = mujoco.MjData(M); D.qpos[:7] = [0, 0, 0.125, 1, 0, 0, 0]; D.qpos[7:] = dp; D.ctrl[:] = dp; mujoco.mj_forward(M, D)
print("newton mj opt", sol.mj_model.opt.timestep, sol.mj_model.opt.integrator, sol.mj_model.opt.iterations, "native", M.opt.integrator, M.opt.iterations)
for k in range(5):
    t = dp + ACT[k]
    tq = c.joint_target_q.numpy(); tq[-14:] = t; c.joint_target_q.assign(tq); D.ctrl[:] = t
    for i in range(4):
        s0.clear_forces(); sol.step(s0, s1, c, None, 0.005); s0, s1 = s1, s0
        mujoco.mj_step(M, D)
        nq = s0.joint_qd.numpy()[6:]; dq = np.abs(nq - D.qvel[6:]).max()
        print(f"{k}.{i} |dqd| {dq:.5f}  ncon newton {sol.mj_data.ncon} native {D.ncon}  ctrl newton {np.abs(sol.mj_data.ctrl - D.ctrl).max():.5f}  qfrc_act {np.abs(sol.mj_data.qfrc_actuator[6:] - D.qfrc_actuator[6:]).max():.5f}")
mjd, mjm = sol.mj_data, sol.mj_model
print("contacts:", mjd.ncon, "dist", np.round(mjd.contact.dist[:mjd.ncon], 4))
print("geoms", sorted(set((int(g1), int(g2)) for g1, g2 in zip(mjd.contact.geom1[:mjd.ncon], mjd.contact.geom2[:mjd.ncon]))))
print("margin of those geoms", [float(mjm.geom_margin[g]) for g in set(mjd.contact.geom2[:mjd.ncon])], "gap", [float(mjm.geom_gap[g]) for g in set(mjd.contact.geom2[:mjd.ncon])])
print("native contacts", D.ncon, "dist", np.round(D.contact.dist[:D.ncon], 4), "margins", [float(M.geom_margin[g]) for g in D.contact.geom2[:D.ncon]])
print("newton geom types", [int(mjm.geom_type[g]) for g in set(mjd.contact.geom2[:mjd.ncon])], "mesh vert counts", [int(mjm.mesh_vertnum[mjm.geom_dataid[g]]) for g in set(mjd.contact.geom2[:mjd.ncon]) if mjm.geom_type[g] == 7])
print("native mesh vert counts", [int(M.mesh_vertnum[M.geom_dataid[g]]) for g in set(D.contact.geom2[:D.ncon]) if M.geom_type[g] == 7], "enableflags newton", mjm.opt.enableflags, "native", M.opt.enableflags)
