"""เทรน Microduck-Walk-Flat-Newton ผ่าน workflow RSL-RL ของ Isaac Lab (รันจาก ~/IsaacLab)
  uv run python ~/repos/microduck_rl/newton_port/isaaclab_task/train.py --task Microduck-Walk-Flat-Newton --num_envs 4096 physics=newton_mjwarp
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import microduck_tasks  # noqa: E402,F401

from isaaclab_rl.entrypoints.backends.train_rsl_rl import run  # noqa: E402

if __name__ == "__main__":
    run(sys.argv[1:])
