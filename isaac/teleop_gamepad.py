"""Open the XLeRobot v0.4 USD in Isaac Sim and teleoperate it with a gamepad."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
from isaacsim import SimulationApp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def newest_usd() -> Path:
    candidates = list((ROOT / "isaac" / "generated").glob("**/xlerobot_v04.usda"))
    if not candidates:
        raise FileNotFoundError("No generated USD found. Run isaac/import.ps1 first.")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--usd", type=Path, default=None, help="USD to open (newest generated USD by default)")
    parser.add_argument("--headless", action="store_true", help="Run without the Isaac window")
    parser.add_argument("--smoke-steps", type=int, default=0, help="Exit after N frames for automated validation")
    return parser.parse_args()


ARGS = parse_args()
APP = SimulationApp({"headless": ARGS.headless})

import carb.input  # noqa: E402
import omni.appwindow  # noqa: E402
from isaacsim.core.api import SimulationContext  # noqa: E402
from isaacsim.core.experimental.objects import GroundPlane  # noqa: E402
from isaacsim.core.prims import Articulation  # noqa: E402
from isaacsim.core.utils.stage import open_stage  # noqa: E402
from xlerobot_twin.teleop import (  # noqa: E402
    A, B, BACK, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT, DPAD_UP, GamepadState, LB,
    LEFT_THUMB, RB, RIGHT_THUMB, START, TeleopController, X, Y, integrate_targets,
)

ARTICULATION_PATH = "/xlerobot_v04_servo_dualwheel/Geometry/base_link"
JOINT_NAMES = (
    "left_wheel_joint", "right_wheel_joint",
    "Rotation_L", "Pitch_L", "Elbow_L", "Wrist_Pitch_L", "Wrist_Roll_L", "Jaw_L",
    "Rotation_R", "Pitch_R", "Elbow_R", "Wrist_Pitch_R", "Wrist_Roll_R", "Jaw_R",
    "head_pan_joint", "head_tilt_joint",
)


class IsaacGamepad:
    """Convert Carb's split-axis inputs to the shared GLFW-style state."""

    _buttons = {
        A: carb.input.GamepadInput.A, B: carb.input.GamepadInput.B,
        X: carb.input.GamepadInput.X, Y: carb.input.GamepadInput.Y,
        LB: carb.input.GamepadInput.LEFT_SHOULDER, RB: carb.input.GamepadInput.RIGHT_SHOULDER,
        BACK: carb.input.GamepadInput.MENU1, START: carb.input.GamepadInput.MENU2,
        LEFT_THUMB: carb.input.GamepadInput.LEFT_STICK,
        RIGHT_THUMB: carb.input.GamepadInput.RIGHT_STICK,
        DPAD_UP: carb.input.GamepadInput.DPAD_UP, DPAD_RIGHT: carb.input.GamepadInput.DPAD_RIGHT,
        DPAD_DOWN: carb.input.GamepadInput.DPAD_DOWN, DPAD_LEFT: carb.input.GamepadInput.DPAD_LEFT,
    }

    def __init__(self) -> None:
        self.interface = carb.input.acquire_input_interface()
        self.gamepad = omni.appwindow.get_default_app_window().get_gamepad(0)

    def value(self, item: carb.input.GamepadInput) -> float:
        return float(self.interface.get_gamepad_value(self.gamepad, item))

    def axis(self, negative: carb.input.GamepadInput, positive: carb.input.GamepadInput) -> float:
        return self.value(positive) - self.value(negative)

    def read(self) -> GamepadState:
        buttons = [0] * 15
        for index, item in self._buttons.items():
            flags = self.interface.get_gamepad_button_flags(self.gamepad, item)
            buttons[index] = int(bool(flags & carb.input.BUTTON_FLAG_DOWN))
        axes = (
            self.axis(carb.input.GamepadInput.LEFT_STICK_LEFT, carb.input.GamepadInput.LEFT_STICK_RIGHT),
            self.axis(carb.input.GamepadInput.LEFT_STICK_UP, carb.input.GamepadInput.LEFT_STICK_DOWN),
            self.axis(carb.input.GamepadInput.RIGHT_STICK_LEFT, carb.input.GamepadInput.RIGHT_STICK_RIGHT),
            self.axis(carb.input.GamepadInput.RIGHT_STICK_UP, carb.input.GamepadInput.RIGHT_STICK_DOWN),
            self.value(carb.input.GamepadInput.LEFT_TRIGGER) * 2.0 - 1.0,
            self.value(carb.input.GamepadInput.RIGHT_TRIGGER) * 2.0 - 1.0,
        )
        return GamepadState(tuple(buttons), axes)


def main() -> None:
    usd = (ARGS.usd or newest_usd()).resolve()
    if not usd.is_file():
        raise FileNotFoundError(usd)
    if not open_stage(str(usd)):
        raise RuntimeError(f"Isaac could not open {usd}")
    APP.update()
    GroundPlane("/World/GroundPlane", positions=[0.0, 0.0, 0.0])
    simulation = SimulationContext(physics_dt=1.0 / 60.0, rendering_dt=1.0 / 60.0)
    simulation.initialize_physics()
    robot = Articulation(ARTICULATION_PATH)
    robot.initialize()
    indices = {name: robot.get_dof_index(name) for name in JOINT_NAMES}
    missing = [name for name, index in indices.items() if index is None or index < 0]
    if missing:
        raise RuntimeError(f"Missing joints in USD: {missing}")

    limits = np.asarray(robot.get_dof_limits())[0]
    positions = np.asarray(robot.get_joint_positions())[0]
    targets = {name: float(positions[index]) for name, index in indices.items()
               if name not in {"left_wheel_joint", "right_wheel_joint"}}
    gamepad = IsaacGamepad()
    controller = TeleopController()
    print(f"USD: {usd}")
    print(f"Validated articulation: {len(indices)} joints")
    print("Hold A: dead-man | B: E-STOP | A+Start: clear/home")
    print("No bumper: left stick base, right stick neck | LB/RB: arm selection")

    simulation.play()
    last = time.monotonic()
    frame = 0
    while APP.is_running():
        now = time.monotonic()
        dt = min(now - last, 0.05)
        last = now
        command = controller.update(gamepad.read(), dt)
        if command.home:
            for name in targets:
                targets[name] = 0.0
        integrate_targets(targets, command, dt)
        linear, angular = command.forward * 0.7, command.turn * 0.55
        wheel_velocity = {
            "left_wheel_joint": (linear - angular * 0.125) / 0.05,
            "right_wheel_joint": (linear + angular * 0.125) / 0.05,
        }
        for name, velocity in wheel_velocity.items():
            robot.set_joint_velocities([[velocity]], joint_indices=[indices[name]])
        for name, target in targets.items():
            index = indices[name]
            low, high = limits[index]
            targets[name] = float(np.clip(target, low, high))
            robot.set_joint_positions([[targets[name]]], joint_indices=[index])
        simulation.step(render=not ARGS.headless)
        frame += 1
        if ARGS.smoke_steps and frame >= ARGS.smoke_steps:
            break
    simulation.stop()
    APP.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        if APP.is_running():
            APP.close()
