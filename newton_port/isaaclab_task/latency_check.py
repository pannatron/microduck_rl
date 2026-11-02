"""ยืนยันว่า latency DR ทำงานจริง: obs ของ joint vel = ค่าของ step ก่อนหน้า, gyro = ค่าปัจจุบันหรือก่อนหน้า (สุ่ม)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, gymnasium as gym
import microduck_tasks
from isaaclab_tasks.utils import parse_env_cfg
cfg = parse_env_cfg("Microduck-Walk-Flat-Newton", num_envs=32)
cfg.observations.policy.enable_corruption = False
cfg.events.push_robot = None
env = gym.make("Microduck-Walk-Flat-Newton", cfg=cfg); obs, _ = env.reset()
robot = env.unwrapped.scene["robot"]; dev = env.unwrapped.device
prev_jv = prev_w = None; jv_prev_err = []; jv_cur_err = []; w_match = []
for k in range(60):
    obs, *_ = env.step(0.3 * torch.randn(32, 14, device=dev))
    o = obs["policy"]
    jv = robot.data.joint_vel.torch.clone(); w = robot.data.root_ang_vel_b.torch.clone()
    if prev_jv is not None and k > 3:
        jv_prev_err.append(((o[:, 20:34] - prev_jv).abs().max(1).values < 1e-4).float().mean().item()); jv_cur_err.append(((o[:, 20:34] - jv).abs().max(1).values < 1e-4).float().mean().item())
        cur = (o[:, 0:3] - w).abs().max(1).values < 1e-4; prv = (o[:, 0:3] - prev_w).abs().max(1).values < 1e-4
        w_match.append((cur.float().mean().item(), prv.float().mean().item()))
    prev_jv, prev_w = jv, w
print("joint_vel obs = previous in %.0f%% of env-steps, = current in %.0f%%" % (100 * sum(jv_prev_err) / len(jv_prev_err), 100 * sum(jv_cur_err) / len(jv_cur_err)))
c = sum(x[0] for x in w_match) / len(w_match); p = sum(x[1] for x in w_match) / len(w_match)
print("gyro obs = current in %.0f%% of env-steps, = previous in %.0f%% (rest: just reset)" % (100 * c, 100 * p))
act = robot.actuators["servos"]; print("actuator", type(act).__name__, "delays sample", act.positions_delay_buffer.time_lags[:12].tolist() if hasattr(act, "positions_delay_buffer") else None)
env.close()
