"""ลงทะเบียน task test bench XL330 แล้วเรียก train ตัวเดิม
testbench_env_cfg.py ใน repo ยังเขียนสำหรับ mjlab รุ่นเก่า (RslRlPpoActorCriticCfg หายไปใน 1.3.0)
→ ใส่ shim ให้ import ผ่าน แล้วสร้าง RL cfg แบบ 1.3.0 เอง (ค่าเดิม: MLP 256-128-64, PPO ชุดเดียวกับ velocity, ไม่ normalize obs)
uv run python playground/train_testbench.py Mjlab-Testbench-XL330 --env.scene.num-envs 4096 --agent.max-iterations 500 --agent.logger tensorboard"""
import mjlab.rl as _rl
from mjlab.rl import RslRlModelCfg, RslRlOnPolicyRunnerCfg, RslRlPpoAlgorithmCfg

if not hasattr(_rl, "RslRlPpoActorCriticCfg"):
    _rl.RslRlPpoActorCriticCfg = lambda **kw: None          # shim: ค่าที่ได้ถูกแทนด้วย cfg ข้างล่าง
    _orig = _rl.RslRlOnPolicyRunnerCfg
    _rl.RslRlOnPolicyRunnerCfg = lambda **kw: None

from mjlab.tasks.registry import register_mjlab_task          # noqa: E402
from mjlab_microduck.tasks.testbench_env_cfg import make_testbench_env_cfg  # noqa: E402

RL = RslRlOnPolicyRunnerCfg(
    actor=RslRlModelCfg(hidden_dims=(256, 128, 64), activation="elu", obs_normalization=False,
                        distribution_cfg={"class_name": "GaussianDistribution", "init_std": 1.0, "std_type": "scalar"}),
    critic=RslRlModelCfg(hidden_dims=(256, 128, 64), activation="elu", obs_normalization=False),
    algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=1.0, use_clipped_value_loss=True, clip_param=0.2, entropy_coef=0.01,
                                   num_learning_epochs=5, num_mini_batches=4, learning_rate=1.0e-3, schedule="adaptive",
                                   gamma=0.99, lam=0.95, desired_kl=0.01, max_grad_norm=1.0),
    experiment_name="testbench", run_name="testbench", save_interval=100, num_steps_per_env=24, max_iterations=500,
)
register_mjlab_task(task_id="Mjlab-Testbench-XL330", env_cfg=make_testbench_env_cfg(),
                    play_env_cfg=make_testbench_env_cfg(play=True), rl_cfg=RL)

from mjlab_microduck.train_cli import main  # noqa: E402

main()
