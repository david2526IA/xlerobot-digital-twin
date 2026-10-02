"""Launch XLeRobot MuJoCo with safe Xbox/Switch gamepad teleoperation."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import glfw
import mujoco
import mujoco.viewer
import numpy as np

from xlerobot_twin.teleop import GamepadState, TeleopController, integrate_targets


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "assets" / "xlerobot" / "xlerobot.xml"


def actuator_ids(model: mujoco.MjModel) -> dict[str, int]:
    return {mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(model.nu)}


def find_gamepad() -> int | None:
    for joystick in range(glfw.JOYSTICK_1, glfw.JOYSTICK_LAST + 1):
        if glfw.joystick_present(joystick) and glfw.joystick_is_gamepad(joystick):
            return joystick
    return None


def read_gamepad(joystick: int) -> GamepadState | None:
    state = glfw.get_gamepad_state(joystick)
    if state is None:
        return None
    return GamepadState(tuple(state.buttons), tuple(state.axes))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", choices=("free", "neck_rgb", "neck_depth"), default="free")
    args = parser.parse_args()

    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)
    ids = actuator_ids(model)
    if not glfw.init():
        raise RuntimeError("GLFW could not initialize; check graphics drivers/display access.")

    joystick = find_gamepad()
    if joystick is not None:
        print(f"Gamepad: {glfw.get_gamepad_name(joystick) or glfw.get_joystick_name(joystick)}")
    else:
        print("No standardized gamepad detected. Hot-plug is enabled.")
    print("Hold A: dead-man | B: E-STOP | A+Start: clear/home")
    print("No bumper: left stick base, right stick neck")
    print("LB/RB: select left/right arm; sticks joints, D-pad roll, triggers gripper")

    targets = {name: 0.0 for name in ids if name not in {"forward", "turn"}}
    controller = TeleopController()
    last_time = time.monotonic()
    last_status = last_time
    last_mode = "safe"

    with mujoco.viewer.launch_passive(model, data) as viewer:
        if args.camera != "free":
            viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FIXED
            viewer.cam.fixedcamid = model.camera(args.camera).id
        while viewer.is_running():
            step_start = time.monotonic()
            dt = min(step_start - last_time, 0.05)
            last_time = step_start
            glfw.poll_events()

            if joystick is None or not glfw.joystick_present(joystick):
                joystick = find_gamepad()
                if joystick is not None:
                    name = glfw.get_gamepad_name(joystick) or glfw.get_joystick_name(joystick)
                    print(f"Gamepad connected: {name}")

            state = read_gamepad(joystick) if joystick is not None else None
            command = controller.update(state or GamepadState((), ()), dt)
            data.ctrl[ids["forward"]] = command.forward * 0.7
            data.ctrl[ids["turn"]] = command.turn * 0.55
            if command.home:
                for name in targets:
                    targets[name] = 0.0
            integrate_targets(targets, command, dt)

            for name, value in targets.items():
                actuator = ids[name]
                low, high = model.actuator_ctrlrange[actuator]
                targets[name] = float(np.clip(value, low, high))
                data.ctrl[actuator] = targets[name]

            if command.mode != last_mode or step_start - last_status > 1.0:
                print(f"mode={command.mode:<10} drive=({command.forward:+.2f}, {command.turn:+.2f})")
                last_mode = command.mode
                last_status = step_start

            mujoco.mj_step(model, data)
            viewer.sync()
            time.sleep(max(0, model.opt.timestep - (time.monotonic() - step_start)))


if __name__ == "__main__":
    main()
