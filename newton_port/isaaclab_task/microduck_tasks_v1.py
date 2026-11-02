"""Microduck-Walk-Flat: เทรนเป็ดเดินบน Isaac Lab + Newton (MuJoCo Warp solver) แบบขนานหลายพัน env

ตั้งใจให้ policy ที่ได้ "สลับกับของ Pollen ได้": obs 61 มิติ ลำดับเดียวกับ microduck_rl
(gyro 3, projected gravity 3, joint pos−default 14, joint vel 14, last action 14, command 13)
และ action = default + 1.0 × output, ลำดับข้อต่อเดียวกัน → export ONNX แล้วรันใน scripts/infer_policy.py ได้ทันที

รางวัลเป็นสูตร velocity มาตรฐานของ Isaac Lab (แบบ G1) ย่อสเกลให้เข้ากับหุ่น 25 ซม. — ไม่ใช่สูตร mjlab ของ Pollen
แอคชูเอเตอร์เป็น PD ธรรมดา (kp 0.55, ±0.96 Nm จาก MJCF) ไม่มีโมเดลมอเตอร์ BAM
"""

import math
import os

import gymnasium as gym
import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
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
        "servos": ImplicitActuatorCfg(
            joint_names_expr=[".*"],
            stiffness=0.55,
            damping=0.053,
            effort_limit_sim=0.96,
            armature=0.0018,
            friction=0.0048,
        ),
    },
)


def zero_pad(env, n: int = 10) -> torch.Tensor:
    """ช่อง command ที่ไม่ใช้ (head_pose 4 + body_pose 6) — ใส่ศูนย์ให้ obs ครบ 61 มิติเหมือน Pollen"""
    return torch.zeros(env.num_envs, n, device=env.device)


@configclass
class MicroduckObs:
    @configclass
    class PolicyCfg(ObsGroup):
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel, noise=Unoise(n_min=-0.1, n_max=0.1))
        projected_gravity = ObsTerm(func=mdp.projected_gravity, noise=Unoise(n_min=-0.03, n_max=0.03))
        joint_pos = ObsTerm(func=mdp.joint_pos_rel, noise=Unoise(n_min=-0.01, n_max=0.01))
        joint_vel = ObsTerm(func=mdp.joint_vel_rel, noise=Unoise(n_min=-0.5, n_max=0.5))
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
    experiment_name = "microduck_walk_newton"
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
