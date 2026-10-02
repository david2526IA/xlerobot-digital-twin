"""Validate the canonical URDF and its parity contract with the MuJoCo twin."""
from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
URDF = ROOT / "robot_description" / "xlerobot_v04.urdf"
MJCF = ROOT / "assets" / "xlerobot" / "xlerobot.xml"
MANIFEST = yaml.safe_load((ROOT / "twin" / "manifest.yaml").read_text(encoding="utf-8"))


def vector(text):
    return [float(value) for value in text.split()]


def main() -> None:
    urdf = ET.parse(URDF).getroot()
    mjcf = ET.parse(MJCF).getroot()
    links = {link.get("name") for link in urdf.findall("link")}
    joints = {joint.get("name"): joint for joint in urdf.findall("joint")}
    moving = {
        name: joint
        for name, joint in joints.items()
        if joint.get("type") in {"revolute", "continuous"}
    }
    required = {
        "left_wheel_joint", "right_wheel_joint",
        "Rotation_L", "Pitch_L", "Elbow_L", "Wrist_Pitch_L", "Wrist_Roll_L", "Jaw_L",
        "Rotation_R", "Pitch_R", "Elbow_R", "Wrist_Pitch_R", "Wrist_Roll_R", "Jaw_R",
        "head_pan_joint", "head_tilt_joint",
    }
    errors = []
    if missing := required - moving.keys():
        errors.append(f"missing moving joints: {sorted(missing)}")
    if len(moving) != 16:
        errors.append(f"expected 16 moving joints, found {len(moving)}")
    if "head_camera_optical_frame" not in links:
        errors.append("missing head_camera_optical_frame")

    left_y = vector(joints["left_wheel_joint"].find("origin").get("xyz"))[1]
    right_y = vector(joints["right_wheel_joint"].find("origin").get("xyz"))[1]
    track = abs(left_y - right_y)
    if not math.isclose(track, MANIFEST["base"]["wheel_physical_track_m"], abs_tol=1e-9):
        errors.append(f"URDF wheel track={track} does not match manifest")

    wheel_links = {
        side: urdf.find(f"link[@name='{side}_wheel_link']")
        for side in ("left", "right")
    }
    physical_radius = MANIFEST["base"]["wheel_physical_radius_m"]
    for side, link in wheel_links.items():
        cylinder = link.find("collision/geometry/cylinder")
        radius = float(cylinder.get("radius"))
        if not math.isclose(radius, physical_radius, abs_tol=1e-9):
            errors.append(f"{side} wheel radius={radius} does not match manifest")

    expected_v04_meshes = {
        "base_chassis.stl", "upper_arm_mount.stl", "neck_refined.stl",
        "drive_side_a_rotor.stl", "drive_side_b_rotor.stl",
    }
    attached_v04 = set()
    for mesh in urdf.findall(".//mesh"):
        filename = mesh.get("filename")
        path = (URDF.parent / filename).resolve()
        if not path.is_file():
            errors.append(f"URDF mesh does not exist: {filename}")
        if "/v04/" in path.as_posix():
            attached_v04.add(path.name)
    if missing := expected_v04_meshes - attached_v04:
        errors.append(f"v0.4 meshes not attached to URDF: {sorted(missing)}")

    mjcf_joints = {joint.get("name") for joint in mjcf.findall(".//joint") if joint.get("name")}
    if missing := required - mjcf_joints:
        errors.append(f"MuJoCo parity missing joints: {sorted(missing)}")
    mjcf_meshes = {mesh.get("name") for mesh in mjcf.findall("./asset/mesh")}
    for name in ("v04_base_chassis", "v04_upper_arm_mount", "v04_neck_refined"):
        if name not in mjcf_meshes:
            errors.append(f"MuJoCo missing integrated mesh {name}")

    if errors:
        raise SystemExit("v0.4 description validation failed:\n" + "\n".join(errors))
    print(
        f"PASS: canonical URDF | links={len(links)} joints={len(joints)} "
        f"moving={len(moving)} track={track:.3f}m tire_radius={physical_radius:.4f}m"
    )


if __name__ == "__main__":
    main()
