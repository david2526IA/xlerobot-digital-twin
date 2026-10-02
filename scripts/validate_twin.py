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
expected = manifest["base"]["wheel_physical_track_m"]
if abs(track - expected) > 1e-9:
    raise SystemExit(f"Wheel track {track} != manifest {expected}")
expected_radius = manifest["base"]["wheel_physical_radius_m"]
for geom_name in ("left_drive_tire", "right_drive_tire"):
    radius = model.geom(geom_name).size[0]
    if abs(radius - expected_radius) > 1e-9:
        raise SystemExit(f"{geom_name} radius {radius} != manifest {expected_radius}")
for geom_name in ("left_drive_tire_visual", "right_drive_tire_visual"):
    geom = model.geom(geom_name)
    if abs(geom.size[0] - expected_radius) > 1e-9 or geom.group >= 3:
        raise SystemExit(f"{geom_name} must expose the complete tire in the default renderer")
for mesh_name in ("v04_base_chassis", "v04_upper_arm_mount", "v04_neck_refined"):
    if mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_MESH, mesh_name) < 0:
        raise SystemExit(f"Missing integrated v0.4 mesh: {mesh_name}")
print(f"PASS: {manifest['robot']['name']} {manifest['robot']['version']} | nu={model.nu} | wheel track={track:.3f} m | tire radius={expected_radius:.4f} m")
