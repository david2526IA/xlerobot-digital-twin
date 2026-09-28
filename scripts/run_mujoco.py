"""Launch the included XLeRobot MuJoCo model with optional Switch-style gamepad control."""
from __future__ import annotations

import time
from pathlib import Path
import mujoco
import mujoco.viewer

import glfw

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "assets" / "xlerobot" / "xlerobot.xml"

def actuator_ids(model: mujoco.MjModel) -> dict[str, int]:
    return {mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(model.nu)}

def main() -> None:
    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)
    ids = actuator_ids(model)
    joystick = glfw.JOYSTICK_1 if glfw.joystick_present(glfw.JOYSTICK_1) else None
    if joystick is not None:
        print(f"Gamepad: {glfw.get_joystick_name(joystick)}")
    else:
        print("No gamepad detected; use MuJoCo's free camera to inspect the model.")

    # Neutral pose; position actuators are commanded in radians, drive motors in [-1, 1].
    targets = {name: 0.0 for name in ids if name not in {"forward", "turn"}}
    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running():
            step_start = time.time()
            if joystick:
                axes = glfw.get_joystick_axes(joystick)
                buttons = glfw.get_joystick_buttons(joystick)
                # Left stick: forward/turn. Buttons A/B: right/left gripper open-close.
                data.ctrl[ids["forward"]] = -axes[1]
                data.ctrl[ids["turn"]] = axes[0]
                targets["Jaw_R"] += 0.025 * (buttons[0] - buttons[1])
                targets["Jaw_L"] += 0.025 * (buttons[2] - buttons[3])
                # Right stick controls neck pan/tilt; see docs for mapping and calibration.
                targets["head_pan"] += 0.02 * axes[2]
                targets["head_tilt"] -= 0.02 * axes[3]
            for name, value in targets.items():
                if name in ids:
                    data.ctrl[ids[name]] = value
            mujoco.mj_step(model, data)
            viewer.sync()
            time.sleep(max(0, model.opt.timestep - (time.time() - step_start)))

if __name__ == "__main__":
    main()
