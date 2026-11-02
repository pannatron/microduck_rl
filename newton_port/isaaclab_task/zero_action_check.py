"""ตรวจก่อนเทรน (AGENTS.md: ท่ายืนต้องเป็นจุดสมดุล): action = 0 ทั้งหมด 3 วินาที เป็ดต้องยืนอยู่ได้ ไม่ล้ม"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, gymnasium as gym
import microduck_tasks
from isaaclab_tasks.utils import parse_env_cfg
cfg = parse_env_cfg("Microduck-Walk-Flat-Newton", num_envs=16)
cfg.events.push_robot = None
env = gym.make("Microduck-Walk-Flat-Newton", cfg=cfg)
env.reset()
robot = env.unwrapped.scene["robot"]
print("joint names", robot.joint_names)
print("default q", [round(float(x), 3) for x in robot.data.default_joint_pos.torch[0]])
deaths = 0
for k in range(150):
    _, _, term, trunc, _ = env.step(torch.zeros(16, 14, device=env.unwrapped.device))
    deaths += int(term.sum())
    if k % 25 == 0:
        z = robot.data.root_pos_w.torch[:, 2]; g = robot.data.projected_gravity_b.torch[:, 2]
        print(f"t={k*0.02:.2f}s z mean {z.mean():.4f} min {z.min():.4f}  grav_z mean {g.mean():.3f}  falls so far {deaths}")
print("falls in 3 s with zero action:", deaths)
env.close()
