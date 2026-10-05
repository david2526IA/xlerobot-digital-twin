"""Gymnasium environment for the included XLeRobot 0.4 MuJoCo twin."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import gymnasium as gym
import mujoco
import numpy as np
from gymnasium import spaces

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "assets" / "xlerobot" / "xlerobot.xml"

ARM_ACTUATORS = (
    "Rotation_L", "Pitch_L", "Elbow_L", "Wrist_Pitch_L", "Wrist_Roll_L", "Jaw_L",
    "Rotation_R", "Pitch_R", "Elbow_R", "Wrist_Pitch_R", "Wrist_Roll_R", "Jaw_R",
    "head_pan", "head_tilt",
)
RIGHT_REACH_ACTUATORS = ("Rotation_R", "Pitch_R", "Elbow_R", "Wrist_Pitch_R")


class XLeRobotReachEnv(gym.Env):
    """Reach a tabletop cube using either arm.

    Action: forward velocity, yaw velocity, then 12 arm/gripper and 2 neck target
    increments. Observation: robot qpos/qvel plus cube and end-effector positions.
    The task intentionally starts as *reach*, not assisted grasping: physics/contact
    must be calibrated before a grasp reward is used for sim-to-real claims.
    """

    metadata = {"render_modes": ["rgb_array", "human"], "render_fps": 30}

    def __init__(
        self,
        render_mode: str | None = None,
        horizon: int = 300,
        domain_randomization: bool = True,
        base_enabled: bool = False,
        action_mode: str = "full",
    ):
        self.model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
        self.data = mujoco.MjData(self.model)
        self.render_mode, self.horizon, self.domain_randomization = render_mode, horizon, domain_randomization
        self.base_enabled = base_enabled
        if action_mode not in {"full", "right_arm"}:
            raise ValueError(f"Unknown action_mode: {action_mode}")
        self.action_mode = action_mode
        self.ids = {mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(self.model.nu)}
        self.cube_joint = self.model.joint("target_cube_free")
        self.left_ee = self.model.site("left_gripper_tip").id
        self.right_ee = self.model.site("right_gripper_tip").id
        # [v, omega, 14 targets]. All actuator actions are normalized to [-1, 1].
        action_size = 16 if action_mode == "full" else len(RIGHT_REACH_ACTUATORS)
        self.action_space = spaces.Box(-1.0, 1.0, shape=(action_size,), dtype=np.float32)
        obs_size = self.model.nq + self.model.nv + 9
        self.observation_space = spaces.Box(-1e6, 1e6, shape=(obs_size,), dtype=np.float32)
        self.renderer = mujoco.Renderer(self.model, height=480, width=640) if render_mode == "rgb_array" else None
        self.steps = 0

    def _observation(self) -> np.ndarray:
        cube = self.data.xpos[self.model.body("target_cube").id]
        ee = np.concatenate((self.data.site_xpos[self.left_ee], self.data.site_xpos[self.right_ee]))
        return np.concatenate((self.data.qpos, self.data.qvel, cube, ee)).astype(np.float32)

    def _info(self) -> dict[str, Any]:
        cube = self.data.xpos[self.model.body("target_cube").id]
        left = self.data.site_xpos[self.left_ee]
        right = self.data.site_xpos[self.right_ee]
        return {"left_distance": float(np.linalg.norm(left - cube)), "right_distance": float(np.linalg.norm(right - cube))}

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)
        mujoco.mj_resetData(self.model, self.data)
        # The first curriculum stage is stationary manipulation. Place the base
        # near the table while preserving a collision-safe gap.
        self.data.qpos[0] = 0.06
        # The operating side is -x. The table edge is at x=-0.27 and physically
        # stops the mobile base before it reaches the manipulation surface.
        # Keep the reach target inside the measured arm workspace from that edge;
        # farther targets belong to a separate navigation/manipulation curriculum.
        y_range = [0.0, 0.15] if self.action_mode == "right_arm" else [-0.15, 0.15]
        # Keep the entire 45 mm cube beyond the -0.27 m table edge.
        cube_xy = self.np_random.uniform([-0.42, y_range[0]], [-0.31, y_range[1]])
        adr = int(self.cube_joint.qposadr[0])
        self.data.qpos[adr:adr + 7] = [cube_xy[0], cube_xy[1], 0.8025, 1, 0, 0, 0]
        self.data.qvel[:] = 0
        if self.domain_randomization:
            cube_geom = self.model.geom("target_cube_geom").id
            self.model.geom_friction[cube_geom, 0] = self.np_random.uniform(0.6, 1.4)
            self.model.geom_rgba[cube_geom, :3] = self.np_random.uniform(0.1, 0.95, size=3)
            self.model.light_pos[0] = self.np_random.uniform([-1.0, -1.0, 1.5], [1.0, 1.0, 3.0])
        mujoco.mj_forward(self.model, self.data)
        self.steps = 0
        return self._observation(), self._info()

    def step(self, action: np.ndarray):
        action = np.asarray(action, dtype=np.float64).clip(-1, 1)
        if self.action_mode == "right_arm":
            reduced_action = action
            action = np.zeros(16, dtype=np.float64)
            for source, name in enumerate(RIGHT_REACH_ACTUATORS):
                action[2 + ARM_ACTUATORS.index(name)] = reduced_action[source]
        # MuJoCo model has torque-like forward/turn tendons. Keep controls conservative.
        self.data.ctrl[self.ids["forward"]] = action[0] * 0.35 if self.base_enabled else 0.0
        self.data.ctrl[self.ids["turn"]] = action[1] * 0.20 if self.base_enabled else 0.0
        for index, name in enumerate(ARM_ACTUATORS, start=2):
            actuator = self.model.actuator(name)
            low, high = self.model.actuator_ctrlrange[actuator.id]
            current = self.data.ctrl[actuator.id]
            self.data.ctrl[actuator.id] = np.clip(current + action[index] * 0.025, low, high)
        for _ in range(8):
            mujoco.mj_step(self.model, self.data)
        self.steps += 1
        info = self._info()
        distance = info["right_distance"] if self.action_mode == "right_arm" else min(info["left_distance"], info["right_distance"])
        # 5 cm is approximately one cube width and measures tip-to-object reach,
        # without requiring the collision meshes to interpenetrate.
        success = distance < 0.05
        reward = -distance + (1.0 if success else 0.0)
        terminated = success
        truncated = self.steps >= self.horizon
        return self._observation(), reward, terminated, truncated, {**info, "success": success}

    def render(self):
        if self.render_mode != "rgb_array":
            return None
        self.renderer.update_scene(self.data, camera="neck_rgb")
        return self.renderer.render()

    def close(self):
        if self.renderer:
            self.renderer.close()
