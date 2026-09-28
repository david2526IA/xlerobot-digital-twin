"""Static checks for the XLeRobot 0.4 MuJoCo twin."""
from __future__ import annotations

from pathlib import Path
import mujoco
import yaml

ROOT = Path(__file__).resolve().parents[1]
manifest = yaml.safe_load((ROOT / "twin" / "manifest.yaml").read_text())
model = mujoco.MjModel.from_xml_path(str(ROOT / "assets" / "xlerobot" / "xlerobot.xml"))

required_actuators = {
    "forward", "turn", "Rotation_L", "Pitch_L", "Elbow_L", "Wrist_Pitch_L", "Wrist_Roll_L", "Jaw_L",
    "Rotation_R", "Pitch_R", "Elbow_R", "Wrist_Pitch_R", "Wrist_Roll_R", "Jaw_R", "head_pan", "head_tilt",
}
available = {mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, i) for i in range(model.nu)}
missing = required_actuators - available
if missing:
    raise SystemExit(f"Missing actuators: {sorted(missing)}")
for camera in ("neck_rgb", "neck_depth"):
    if mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, camera) < 0:
        raise SystemExit(f"Missing camera: {camera}")
for site in ("left_gripper_tip", "right_gripper_tip"):
    if mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, site) < 0:
        raise SystemExit(f"Missing end-effector site: {site}")
left = model.body("left_wheel").pos
right = model.body("right_wheel").pos
track = abs(left[1] - right[1])
expected = manifest["base"]["wheel_track_m"]
if abs(track - expected) > 1e-9:
    raise SystemExit(f"Wheel track {track} != manifest {expected}")
print(f"PASS: {manifest['robot']['name']} {manifest['robot']['version']} | nu={model.nu} | wheel track={track:.3f} m")
