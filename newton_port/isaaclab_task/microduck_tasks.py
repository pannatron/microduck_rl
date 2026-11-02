"""Microduck-Walk-Flat: เทรนเป็ดเดินบน Isaac Lab + Newton (MuJoCo Warp solver) แบบขนานหลายพัน env

ตั้งใจให้ policy ที่ได้ "สลับกับของ Pollen ได้": obs 61 มิติ ลำดับเดียวกับ microduck_rl
(gyro 3, projected gravity 3, joint pos−default 14, joint vel 14, last action 14, command 13)
และ action = default + 1.0 × output, ลำดับข้อต่อเดียวกัน → export ONNX แล้วรันใน scripts/infer_policy.py ได้ทันที

รางวัลเป็นสูตร velocity มาตรฐานของ Isaac Lab (แบบ G1) ย่อสเกลให้เข้ากับหุ่น 25 ซม. — ไม่ใช่สูตร mjlab ของ Pollen
แอคชูเอเตอร์เป็น PD ธรรมดา (kp 0.55, ±0.96 Nm จาก MJCF) ไม่มีโมเดลมอเตอร์ BAM

LATENCY_DR=1 (ค่าเริ่มต้น) ใส่ความหน่วงแบบเดียวกับ mjlab ของ Pollen:
  - คำสั่งมอเตอร์ช้า 3–6 physics step (15–30 ms) สุ่มใหม่ทุก reset          (BAM delay_min/max_lag)
  - IMU (gyro + gravity) ช้า 0–1 control step (0–20 ms) สุ่มใหม่เฉลี่ยทุก 64 step  (delay_max_lag=1, update_period=64)
  - joint vel ช้า 1 control step ตายตัว (firmware Dynamixel เฉลี่ยความเร็วย้อนหลัง)
LATENCY_DR=0 = เวอร์ชันแรก (ไม่มีความหน่วง) ไว้เทียบ
"""

import math
import os

import gymnasium as gym
import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import DelayedPDActuatorCfg, ImplicitActuatorCfg
from isaaclab.managers import ManagerTermBase
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.utils import configclass
from isaaclab.utils.noise import UniformNoiseCfg as Unoise
from isaaclab_newton.sim.schemas import NewtonArticulationCfg
from isaaclab_rl.rsl_rl import RslRlMLPModelCfg, RslRlOnPolicyRunnerCfg, RslRlPpoAlgorithmCfg
from isaaclab_tasks.core.velocity import mdp
from isaaclab_tasks.core.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg

ROBOT_DIR = os.path.expanduser("~/repos/microduck_rl/src/mjlab_microduck/robot/microduck")
USD_DIR = os.path.expanduser("~/repos/microduck_rl/newton_port/isaaclab_task/generated/microduck_groundcontact")

# ลำดับข้อต่อของ Pollen (ctrl idx = joint idx): ขาซ้าย 0–4, คอ/หัว 5–8, ขาขวา 9–13
JOINTS = ["left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
          "neck_pitch", "head_pitch", "head_yaw", "head_roll",
          "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle"]
DEFAULT_POSE = [0.0, -0.0872665, -0.457924, -0.004940, 0.452984, 0.3490659, 0.3490659, 0.0, 0.0,
                0.0, 0.0872665, 0.457924, 0.004940, -0.452984]
FEET = "ankle_(left|right)"   # body ที่มี foot collision
TRUNK = "trunk_base"
HEAD = ["neck_pitch", "head_pitch", "head_yaw", "head_roll"]


def _patch_mjcf_importer():
    """MJCF importer ใส่ PhysX joint schema ที่ไม่มีในเครื่องแบบ Newton-only → ข้ามตัวที่ใส่ไม่ได้ (ท่าเดียวกับ RP1)"""
    try:
        from isaacsim.asset.importer.utils.impl import importer_utils as iu
    except ImportError:
        return
    orig = iu.add_joint_schemas

    def add_joint_schemas(stage):
        try:
            orig(stage)
        except Exception:
            from pxr import UsdPhysics

            for prim in stage.Traverse():
                for kind, inst in ((UsdPhysics.RevoluteJoint, "angular"), (UsdPhysics.PrismaticJoint, "linear")):
                    if prim.IsA(kind) and not prim.HasAPI(UsdPhysics.DriveAPI, inst):
                        UsdPhysics.DriveAPI.Apply(prim, inst)

    iu.add_joint_schemas = add_joint_schemas


_patch_mjcf_importer()

MICRODUCK_CFG = ArticulationCfg(
    spawn=sim_utils.MjcfFileCfg(
        asset_path=f"{ROBOT_DIR}/robot_groundcontact.xml",
        usd_dir=USD_DIR,
        self_collision=False,
        fix_base=False,
        activate_contact_sensors=True,
        articulation_props=[NewtonArticulationCfg(self_collision_enabled=False)],
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.125),
        joint_pos=dict(zip(JOINTS, DEFAULT_POSE)),
        joint_vel={".*": 0.0},
    ),
    soft_joint_pos_limit_factor=0.95,
    joint_ordering=tuple(JOINTS),
    actuators={
        # XL330 ใน MJCF: position kp 0.55, forcerange ±0.96 Nm, damping 0.053, armature 0.0018, frictionloss 0.0048
        "servos": DelayedPDActuatorCfg(
            joint_names_expr=[".*"],
            stiffness=0.55,
            damping=0.053,
            effort_limit=0.96,
            effort_limit_sim=0.96,
            armature=0.0018,
            friction=0.0048,
            min_delay=3,          # physics step (5 ms) → 15–30 ms เหมือน BAM delay_min/max_lag ของ Pollen
            max_delay=6,
        ) if os.environ.get("LATENCY_DR", "1") == "1" else ImplicitActuatorCfg(
            joint_names_expr=[".*"],
            stiffness=0.55,
            damping=0.053,
            effort_limit_sim=0.96,
            armature=0.0018,
            friction=0.0048,
        ),
    },
)


LATENCY_DR = os.environ.get("LATENCY_DR", "1") == "1"


class DelayedObs(ManagerTermBase):
    """obs ที่ช้าไป lag control step (lag ∈ [min_lag, max_lag] ต่อ env)

    เก็บประวัติ max_lag+1 ค่า; ทุก step แต่ละ env มีโอกาส 1/update_period ที่จะสุ่ม lag ใหม่
    (update_period=0 = สุ่มครั้งเดียวตอน reset) — เลียนแบบ delay_*_lag ของ mjlab
    """

    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        p = cfg.params
        self.func, self.min_lag, self.max_lag, self.period = p["func"], p["min_lag"], p["max_lag"], p["update_period"]
        self.hist = None
        self.lag = torch.randint(self.min_lag, self.max_lag + 1, (env.num_envs,), device=env.device)

    def reset(self, env_ids=None):
        if env_ids is None:
            env_ids = slice(None)
        if self.hist is not None:
            self.hist[:, env_ids] = 0.0
            self.fresh[env_ids] = True
        n = self.lag[env_ids].numel()
        self.lag[env_ids] = torch.randint(self.min_lag, self.max_lag + 1, (n,), device=self.lag.device)

    def __call__(self, env, func, min_lag, max_lag, update_period):
        x = func(env)
        if self.hist is None:
            self.hist = torch.zeros(self.max_lag + 1, *x.shape, device=x.device)
            self.fresh = torch.ones(x.shape[0], dtype=torch.bool, device=x.device)
        self.hist = torch.roll(self.hist, 1, 0)
        self.hist[0] = x
        f = self.fresh                                   # หลัง reset ยังไม่มีอดีต → เติมด้วยค่าปัจจุบัน
        if f.any():
            self.hist[:, f] = x[f]
            self.fresh[:] = False
        if self.period > 0:
            m = torch.rand(x.shape[0], device=x.device) < 1.0 / self.period
            if m.any():
                self.lag[m] = torch.randint(self.min_lag, self.max_lag + 1, (int(m.sum()),), device=x.device)
        return self.hist[self.lag, torch.arange(x.shape[0], device=x.device)]


def delayed(func, min_lag, max_lag, update_period, noise):
    if not LATENCY_DR:
        return ObsTerm(func=func, noise=noise)
    return ObsTerm(func=DelayedObs, noise=noise,
                   params={"func": func, "min_lag": min_lag, "max_lag": max_lag, "update_period": update_period})


def zero_pad(env, n: int = 10) -> torch.Tensor:
    """ช่อง command ที่ไม่ใช้ (head_pose 4 + body_pose 6) — ใส่ศูนย์ให้ obs ครบ 61 มิติเหมือน Pollen"""
    return torch.zeros(env.num_envs, n, device=env.device)


@configclass
class MicroduckObs:
    @configclass
    class PolicyCfg(ObsGroup):
        base_ang_vel = delayed(mdp.base_ang_vel, 0, 1, 64, Unoise(n_min=-0.1, n_max=0.1))
        projected_gravity = delayed(mdp.projected_gravity, 0, 1, 64, Unoise(n_min=-0.03, n_max=0.03))
        joint_pos = ObsTerm(func=mdp.joint_pos_rel, noise=Unoise(n_min=-0.01, n_max=0.01))
        joint_vel = delayed(mdp.joint_vel_rel, 1, 1, 0, Unoise(n_min=-0.5, n_max=0.5))
        actions = ObsTerm(func=mdp.last_action)
        velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
        pose_commands = ObsTerm(func=zero_pad)

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class MicroduckRewards:
    termination_penalty = RewTerm(func=mdp.is_terminated, weight=-200.0)
    # std ≈ error ที่ยังสนใจ: เป็ดเดินแค่ 0.1–0.4 m/s → std 0.15 (G1 ใช้ 0.5)
    track_lin_vel_xy_exp = RewTerm(func=mdp.track_lin_vel_xy_yaw_frame_exp, weight=1.5,
                                   params={"command_name": "base_velocity", "std": 0.15})
    track_ang_vel_z_exp = RewTerm(func=mdp.track_ang_vel_z_world_exp, weight=1.0,
                                  params={"command_name": "base_velocity", "std": 0.4})
    feet_air_time = RewTerm(func=mdp.feet_air_time_positive_biped, weight=0.5,
                            params={"command_name": "base_velocity", "threshold": 0.2,
                                    "sensor_cfg": SceneEntityCfg("contact_forces", body_names=FEET)})
    feet_slide = RewTerm(func=mdp.feet_slide, weight=-0.5,
                         params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=FEET),
                                 "asset_cfg": SceneEntityCfg("robot", body_names=FEET)})
    lin_vel_z_l2 = RewTerm(func=mdp.lin_vel_z_l2, weight=-2.0)
    ang_vel_xy_l2 = RewTerm(func=mdp.ang_vel_xy_l2, weight=-0.05)
    flat_orientation_l2 = RewTerm(func=mdp.flat_orientation_l2, weight=-2.0)
    action_rate_l2 = RewTerm(func=mdp.action_rate_l2, weight=-0.05)
    dof_acc_l2 = RewTerm(func=mdp.joint_acc_l2, weight=-1.0e-6)
    dof_pos_limits = RewTerm(func=mdp.joint_pos_limits, weight=-1.0)
    head_still = RewTerm(func=mdp.joint_deviation_l1, weight=-0.5,
                         params={"asset_cfg": SceneEntityCfg("robot", joint_names=HEAD)})
    hip_yaw_roll = RewTerm(func=mdp.joint_deviation_l1, weight=-0.2,
                           params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_hip_yaw", ".*_hip_roll"])})


@configclass
class MicroduckWalkEnvCfg(LocomotionVelocityRoughEnvCfg):
    observations: MicroduckObs = MicroduckObs()
    rewards: MicroduckRewards = MicroduckRewards()

    def __post_init__(self):
        super().__post_init__()
        # ---- physics: MuJoCo Warp ผ่าน Newton, ใช้ contact ของ MuJoCo (ค่า default ของ preset จูนมาเพื่อหุ่นขนาดคน)
        nm = self.sim.physics.newton_mjwarp
        nm.solver_cfg.use_mujoco_contacts = True
        nm.collision_cfg = None                  # ใช้ collision ของ MuJoCo แทน pipeline ของ Newton
        nm.solver_cfg.njmax = 200
        nm.solver_cfg.nconmax = 40
        nm.solver_cfg.integrator = "implicitfast"
        nm.solver_cfg.cone = "pyramidal"
        nm.num_substeps = 1                      # dt 0.005 เหมือน mjlab
        self.sim.physics.default = nm
        self.sim.use_newton_actuators = False    # DelayedPD คำนวณใน Isaac Lab ทุก physics step
        self.sim.dt = 0.005
        self.decimation = 4                      # policy 50 Hz
        self.episode_length_s = 20.0
        # ---- scene
        self.scene.robot = MICRODUCK_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.contact_forces.prim_path = "{ENV_REGEX_NS}/Robot/.*"
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None
        self.scene.height_scanner = None
        self.scene.env_spacing = 1.0
        self.curriculum.terrain_levels = None
        # ---- actions: target = default + 1.0 × action (เหมือน Pollen)
        self.actions.joint_pos.scale = 1.0
        self.actions.joint_pos.joint_names = JOINTS
        self.actions.joint_pos.preserve_order = True
        # ---- commands: ช่วงเดียวกับ microduck_rl, สั่ง ωz ตรง ๆ (ไม่ใช้ heading)
        c = self.commands.base_velocity
        c.heading_command = False
        c.rel_heading_envs = 0.0
        c.rel_standing_envs = 0.1
        c.resampling_time_range = (5.0, 10.0)
        c.ranges.lin_vel_x = (-0.3, 0.4)
        c.ranges.lin_vel_y = (-0.2, 0.2)
        c.ranges.ang_vel_z = (-1.0, 1.0)
        c.debug_vis = False
        # ---- terminations: ล้ม = ลำตัวเอียงเกิน 1 rad หรือ trunk ต่ำกว่า 7 ซม. (ยืนปกติ ~11.6 ซม.)
        self.terminations.base_contact = None
        self.terminations.bad_orientation = DoneTerm(func=mdp.bad_orientation, params={"limit_angle": 1.0})
        self.terminations.base_height = DoneTerm(func=mdp.root_height_below_minimum, params={"minimum_height": 0.07})
        # ---- events / domain randomization (เบา ๆ)
        ev = self.events
        ev.physics_material.params["static_friction_range"] = (0.6, 1.2)
        ev.physics_material.params["dynamic_friction_range"] = (0.5, 1.0)
        ev.add_base_mass.params["asset_cfg"].body_names = TRUNK
        ev.add_base_mass.params["mass_distribution_params"] = (1 / 1.1, 1.1)
        ev.base_com = None
        ev.base_external_force_torque = None
        ev.reset_base.params["pose_range"] = {"x": (-0.3, 0.3), "y": (-0.3, 0.3), "yaw": (-3.14, 3.14)}
        ev.reset_base.params["velocity_range"] = {k: (-0.05, 0.05) for k in ("x", "y", "z", "roll", "pitch", "yaw")}
        ev.reset_robot_joints = EventTerm(func=mdp.reset_joints_by_offset, mode="reset",
                                          params={"position_range": (-0.05, 0.05), "velocity_range": (0.0, 0.0)})
        ev.push_robot.interval_range_s = (6.0, 10.0)
        ev.push_robot.params["velocity_range"] = {"x": (-0.2, 0.2), "y": (-0.2, 0.2)}


@configclass
class MicroduckWalkPPOCfg(RslRlOnPolicyRunnerCfg):
    """ค่าเดียวกับ microduck_rl: MLP 512-256-128 ELU, PPO clip 0.2, adaptive lr kl 0.01, obs normalization ON"""
    num_steps_per_env = 24
    max_iterations = 2000
    save_interval = 250
    experiment_name = "microduck_walk_newton" + ("_latency" if LATENCY_DR else "")
    logger = "tensorboard"
    obs_groups = {"actor": ["policy"], "critic": ["policy"]}
    actor = RslRlMLPModelCfg(hidden_dims=[512, 256, 128], activation="elu", obs_normalization=True,
                             distribution_cfg=RslRlMLPModelCfg.GaussianDistributionCfg(init_std=1.0))
    critic = RslRlMLPModelCfg(hidden_dims=[512, 256, 128], activation="elu", obs_normalization=True)
    algorithm = RslRlPpoAlgorithmCfg(value_loss_coef=1.0, use_clipped_value_loss=True, clip_param=0.2,
                                     entropy_coef=0.01, num_learning_epochs=5, num_mini_batches=4,
                                     learning_rate=1.0e-3, schedule="adaptive", gamma=0.99, lam=0.95,
                                     desired_kl=0.01, max_grad_norm=1.0)


gym.register(id="Microduck-Walk-Flat-Newton", entry_point=ManagerBasedRLEnv, disable_env_checker=True,
             kwargs={"env_cfg_entry_point": f"{__name__}:MicroduckWalkEnvCfg",
                     "rsl_rl_cfg_entry_point": f"{__name__}:MicroduckWalkPPOCfg"})


# ================================================================ สัปดาห์ 8 · ท่าใหม่: หันหัวตามเป้าขณะเดิน
# ใช้ช่อง head_pose 4 ช่องของ obs (เดิมเป็นศูนย์) = [neck_pitch, head_pitch, head_yaw, head_roll] เป้าหมายเทียบกับท่า default
HEAD_IDS = [5, 6, 7, 8]
HEAD_RANGE = {"pitch": 0.4, "yaw": 0.8}       # rad
HEAD_RESAMPLE_S = (2.0, 4.0)


class HeadTargetObs(ManagerTermBase):
    """สุ่มเป้าหัว (head_pitch, head_yaw) ต่อ env ทุก 2–4 s แล้วคืนเป็น obs 4 ช่อง; เก็บไว้ที่ env.head_target ให้ reward อ่าน"""

    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        n = env.num_envs
        env.head_target = torch.zeros(n, 4, device=env.device)
        self.timer = torch.zeros(n, device=env.device)

    def _resample(self, ids):
        env = self._env; k = len(ids)
        t = torch.zeros(k, 4, device=env.device)
        t[:, 1] = (torch.rand(k, device=env.device) * 2 - 1) * HEAD_RANGE["pitch"]
        t[:, 2] = (torch.rand(k, device=env.device) * 2 - 1) * HEAD_RANGE["yaw"]
        still = torch.rand(k, device=env.device) < 0.2           # 20% = มองตรง (ต้องฝึกค่าศูนย์ด้วย)
        t[still] = 0.0
        env.head_target[ids] = t
        lo, hi = HEAD_RESAMPLE_S
        self.timer[ids] = lo + torch.rand(k, device=env.device) * (hi - lo)

    def reset(self, env_ids=None):
        ids = torch.arange(self._env.num_envs, device=self._env.device) if env_ids is None else torch.as_tensor(env_ids, device=self._env.device)
        if len(ids):
            self._resample(ids)

    def __call__(self, env):
        self.timer -= env.step_dt
        due = (self.timer <= 0).nonzero(as_tuple=False).squeeze(-1)
        if len(due):
            self._resample(due)
        return env.head_target


def head_tracking(env, std: float = 0.15):
    """exp(−‖q_head − (default + target)‖² / std²): ใกล้เป้า = ได้ 1"""
    if not hasattr(env, "head_target"):
        return torch.zeros(env.num_envs, device=env.device)
    robot = env.scene["robot"]
    q = robot.data.joint_pos.torch[:, HEAD_IDS] - robot.data.default_joint_pos.torch[:, HEAD_IDS]
    err = torch.sum(torch.square(q - env.head_target), dim=1)
    return torch.exp(-err / std ** 2)


HEAD_V = os.environ.get("HEAD_V", "2")       # 1 = ลืมลบ head_still (reward ขัดกัน), 2 = ลบแล้ว


@configclass
class MicroduckHeadObs(MicroduckObs):
    @configclass
    class PolicyCfg(MicroduckObs.PolicyCfg):
        pose_commands = ObsTerm(func=zero_pad, params={"n": 6})

        def __post_init__(self):
            super().__post_init__()
            # ลำดับต้องเป็น ... velocity(3), head_pose(4), body_pose(6) — แทรก head ก่อน pose_commands
            self.head_commands = ObsTerm(func=HeadTargetObs)
            terms = {k: getattr(self, k) for k in ["base_ang_vel", "projected_gravity", "joint_pos", "joint_vel", "actions",
                                                    "velocity_commands", "head_commands", "pose_commands"]}
            for k in terms:
                delattr(self, k)
            for k, v in terms.items():
                setattr(self, k, v)

    policy: PolicyCfg = PolicyCfg()


@configclass
class MicroduckHeadEnvCfg(MicroduckWalkEnvCfg):
    observations: MicroduckHeadObs = MicroduckHeadObs()

    def __post_init__(self):
        super().__post_init__()
        self.rewards.head_tracking = RewTerm(func=head_tracking, weight=1.5, params={"std": 0.15})
        if HEAD_V == "2":
            self.rewards.head_still = None


@configclass
class MicroduckHeadPPOCfg(MicroduckWalkPPOCfg):
    experiment_name = f"microduck_head_v{HEAD_V}"


gym.register(id="Microduck-HeadTrack-Flat-Newton", entry_point=ManagerBasedRLEnv, disable_env_checker=True,
             kwargs={"env_cfg_entry_point": f"{__name__}:MicroduckHeadEnvCfg",
                     "rsl_rl_cfg_entry_point": f"{__name__}:MicroduckHeadPPOCfg"})
