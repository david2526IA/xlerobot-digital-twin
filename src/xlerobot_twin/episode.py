"""Portable telemetry contract for simulated XLeRobot demonstrations.

The contract deliberately avoids any robot transport. It gives MuJoCo, Isaac
Lab and a future hardware bridge the same episode fields, units and action
order without claiming that the physical robot has been calibrated.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


ACTION_NAMES = (
    "base_forward", "base_turn",
    "Rotation_L", "Pitch_L", "Elbow_L", "Wrist_Pitch_L", "Wrist_Roll_L", "Jaw_L",
    "Rotation_R", "Pitch_R", "Elbow_R", "Wrist_Pitch_R", "Wrist_Roll_R", "Jaw_R",
    "head_pan", "head_tilt",
)


@dataclass
class EpisodeRecorder:
    """Collect a time-aligned episode using the stable 16-action contract."""

    control_dt_s: float
    source: str
    observations: list[np.ndarray] = field(default_factory=list)
    actions: list[np.ndarray] = field(default_factory=list)
    rewards: list[float] = field(default_factory=list)
    qpos: list[np.ndarray] = field(default_factory=list)
    qvel: list[np.ndarray] = field(default_factory=list)
    neck_rgb: list[np.ndarray] = field(default_factory=list)

    def append(
        self,
        *,
        observation: np.ndarray,
        action: np.ndarray,
        reward: float,
        qpos: np.ndarray,
        qvel: np.ndarray,
        image: np.ndarray | None = None,
    ) -> None:
        action = np.asarray(action, dtype=np.float32)
        if action.shape != (len(ACTION_NAMES),):
            raise ValueError(f"Expected {len(ACTION_NAMES)} actions, got {action.shape}")
        self.observations.append(np.asarray(observation, dtype=np.float32).copy())
        self.actions.append(action.copy())
        self.rewards.append(float(reward))
        self.qpos.append(np.asarray(qpos, dtype=np.float32).copy())
        self.qvel.append(np.asarray(qvel, dtype=np.float32).copy())
        if image is not None:
            self.neck_rgb.append(np.asarray(image, dtype=np.uint8).copy())

    def payload(self, *, task: str, success: bool | None = None) -> dict[str, Any]:
        length = len(self.actions)
        result: dict[str, Any] = {
            "schema_version": np.asarray("xlerobot_episode_v1"),
            "source": np.asarray(self.source),
            "task": np.asarray(task),
            "control_dt_s": np.asarray(self.control_dt_s, dtype=np.float32),
            "timestamp_s": np.arange(length, dtype=np.float32) * self.control_dt_s,
            "action": np.asarray(self.actions, dtype=np.float32),
            "action_names": np.asarray(ACTION_NAMES),
            "observation": np.asarray(self.observations, dtype=np.float32),
            "qpos": np.asarray(self.qpos, dtype=np.float32),
            "qvel": np.asarray(self.qvel, dtype=np.float32),
            "reward": np.asarray(self.rewards, dtype=np.float32),
        }
        if success is not None:
            result["success"] = np.asarray(success)
        if self.neck_rgb:
            if len(self.neck_rgb) != length:
                raise ValueError("Every step must contain neck_rgb, or none may contain it")
            result["neck_rgb"] = np.asarray(self.neck_rgb, dtype=np.uint8)
        return result
