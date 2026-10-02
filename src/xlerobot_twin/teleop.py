"""Safe, simulator-independent Xbox/Switch gamepad mapping for XLeRobot."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


# GLFW standardized gamepad order (Xbox, Switch Pro and compatible pads).
A, B, X, Y = 0, 1, 2, 3
LB, RB, BACK, START = 4, 5, 6, 7
LEFT_THUMB, RIGHT_THUMB = 8, 9
DPAD_UP, DPAD_RIGHT, DPAD_DOWN, DPAD_LEFT = 11, 12, 13, 14
LEFT_X, LEFT_Y, RIGHT_X, RIGHT_Y, LEFT_TRIGGER, RIGHT_TRIGGER = range(6)

ARM_JOINTS = {
    "left": ("Rotation_L", "Pitch_L", "Elbow_L", "Wrist_Pitch_L", "Wrist_Roll_L", "Jaw_L"),
    "right": ("Rotation_R", "Pitch_R", "Elbow_R", "Wrist_Pitch_R", "Wrist_Roll_R", "Jaw_R"),
}


def shaped_axis(value: float, deadzone: float = 0.12) -> float:
    """Apply a dead zone and squared response while preserving full scale."""
    value = float(np.clip(value, -1.0, 1.0))
    magnitude = abs(value)
    if magnitude <= deadzone:
        return 0.0
    normalized = (magnitude - deadzone) / (1.0 - deadzone)
    return float(np.copysign(normalized * normalized, value))


def trigger(value: float) -> float:
    """Convert GLFW's [-1, 1] trigger convention to [0, 1]."""
    return float(np.clip((value + 1.0) * 0.5, 0.0, 1.0))


@dataclass(frozen=True)
class GamepadState:
    buttons: tuple[int, ...]
    axes: tuple[float, ...]

    def button(self, index: int) -> bool:
        return index < len(self.buttons) and bool(self.buttons[index])

    def axis(self, index: int) -> float:
        return self.axes[index] if index < len(self.axes) else 0.0


@dataclass
class TeleopCommand:
    forward: float = 0.0
    turn: float = 0.0
    joint_velocity: dict[str, float] = field(default_factory=dict)
    mode: str = "safe"
    estop: bool = False
    home: bool = False


class TeleopController:
    """Map a standardized pad to the base, arms, grippers and neck safely."""

    def __init__(self, deadzone: float = 0.12):
        self.deadzone = deadzone
        self.estop_latched = False

    def update(self, state: GamepadState, dt: float) -> TeleopCommand:
        del dt  # Commands are velocities; integration happens in the simulator adapter.
        if state.button(B):
            self.estop_latched = True

        deadman = state.button(A)
        home = deadman and state.button(START)
        if home:
            self.estop_latched = False

        if self.estop_latched:
            return TeleopCommand(mode="E-STOP", estop=True)
        if not deadman:
            return TeleopCommand(mode="safe")
        if home:
            return TeleopCommand(mode="home", home=True)

        lx = shaped_axis(state.axis(LEFT_X), self.deadzone)
        ly = shaped_axis(state.axis(LEFT_Y), self.deadzone)
        rx = shaped_axis(state.axis(RIGHT_X), self.deadzone)
        ry = shaped_axis(state.axis(RIGHT_Y), self.deadzone)
        selected = []
        if state.button(LB):
            selected.append("left")
        if state.button(RB):
            selected.append("right")

        if not selected:
            return TeleopCommand(
                forward=-ly,
                turn=lx,
                joint_velocity={"head_pan": rx * 0.9, "head_tilt": -ry * 0.7},
                mode="base+head",
            )

        dpad_roll = float(state.button(DPAD_RIGHT)) - float(state.button(DPAD_LEFT))
        jaw = trigger(state.axis(RIGHT_TRIGGER)) - trigger(state.axis(LEFT_TRIGGER))
        velocity: dict[str, float] = {}
        for side in selected:
            rotation, pitch, elbow, wrist_pitch, wrist_roll, gripper = ARM_JOINTS[side]
            velocity.update(
                {
                    rotation: lx,
                    pitch: -ly,
                    elbow: -ry,
                    wrist_pitch: rx,
                    wrist_roll: dpad_roll * 1.2,
                    gripper: jaw * 1.5,
                }
            )
        return TeleopCommand(joint_velocity=velocity, mode="+".join(selected) + " arm")


def integrate_targets(targets: dict[str, float], command: TeleopCommand, dt: float) -> None:
    for name, velocity in command.joint_velocity.items():
        if name in targets:
            targets[name] += velocity * dt
