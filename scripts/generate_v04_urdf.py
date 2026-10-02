"""Generate the canonical XLeRobot 0.4 servo dual-wheel URDF."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "robot_description" / "xlerobot_v04.urdf"


def origin(parent, xyz="0 0 0", rpy="0 0 0"):
    ET.SubElement(parent, "origin", xyz=xyz, rpy=rpy)


def material(parent, name, rgba):
    node = ET.SubElement(parent, "material", name=name)
    ET.SubElement(node, "color", rgba=rgba)


def inertial(link, mass, xyz="0 0 0", inertia=(0.001, 0.001, 0.001)):
    node = ET.SubElement(link, "inertial")
    origin(node, xyz)
    ET.SubElement(node, "mass", value=str(mass))
    ixx, iyy, izz = inertia
    ET.SubElement(node, "inertia", ixx=str(ixx), ixy="0", ixz="0", iyy=str(iyy), iyz="0", izz=str(izz))


def mesh_visual(link, filename, xyz="0 0 0", rpy="0 0 0", scale=None, mat="white"):
    node = ET.SubElement(link, "visual")
    origin(node, xyz, rpy)
    geometry = ET.SubElement(node, "geometry")
    attrs = {"filename": filename}
    if scale:
        attrs["scale"] = scale
    ET.SubElement(geometry, "mesh", **attrs)
    ET.SubElement(node, "material", name=mat)


def primitive(link, tag, attrs, xyz="0 0 0", rpy="0 0 0", collision=False, mat="white"):
    node = ET.SubElement(link, "collision" if collision else "visual")
    origin(node, xyz, rpy)
    geometry = ET.SubElement(node, "geometry")
    ET.SubElement(geometry, tag, **attrs)
    if not collision:
        ET.SubElement(node, "material", name=mat)


def joint(robot, name, kind, parent_name, child_name, xyz="0 0 0", rpy="0 0 0", axis=None, limits=None):
    node = ET.SubElement(robot, "joint", name=name, type=kind)
    ET.SubElement(node, "parent", link=parent_name)
    ET.SubElement(node, "child", link=child_name)
    origin(node, xyz, rpy)
    if axis:
        ET.SubElement(node, "axis", xyz=axis)
    if limits:
        ET.SubElement(node, "limit", **{key: str(value) for key, value in limits.items()})
    ET.SubElement(node, "dynamics", damping="0.6" if kind == "revolute" else "0.03", friction="0.052")


def arm(robot, side, base_xyz, base_rpy):
    suffix = "L" if side == "left" else "R"
    prefix = f"{side}_arm"
    base = ET.SubElement(robot, "link", name=f"{prefix}_base_link")
    inertial(base, 0.147, "0.013718 0 0.033484", (0.000115, 0.000136, 0.000130))
    mesh_visual(base, "../assets/xlerobot/assets/Base.stl")
    mesh_visual(base, "../assets/xlerobot/assets/Base_Motor.stl", mat="motor")
    primitive(base, "box", {"size": "0.09 0.08 0.08"}, collision=True)
    joint(robot, f"{prefix}_mount_joint", "fixed", "base_link", base.attrib["name"], base_xyz, base_rpy)

    specs = [
        ("rotation", f"Rotation_{suffix}", "0 -0.0452 0.0165", "1.5708 0 0", "0 -1 0", -2.16, 2.16,
         "Rotation_Pitch.stl", "Rotation_Pitch_Motor.stl", 0.100006, (0.000084, 0.000081, 0.000024)),
        ("upper", f"Pitch_{suffix}", "0 0.1025 0.0306", "1.5708 0 0", "-1 0 0", -0.22, 3.37,
         "Upper_Arm.stl", "Upper_Arm_Motor.stl", 0.103, (0.000041, 0.000147, 0.000142)),
        ("lower", f"Elbow_{suffix}", "0 0.11257 0.028", "-1.5708 0 0", "1 0 0", -0.22, 3.14,
         "Lower_Arm.stl", "Lower_Arm_Motor.stl", 0.104, (0.000029, 0.000160, 0.000145)),
        ("wrist_pitch", f"Wrist_Pitch_{suffix}", "0 0.0052 0.1349", "-1.5708 0 0", "1 0 0", -1.65806, 1.65806,
         "Wrist_Pitch_Roll.stl", "Wrist_Pitch_Roll_Motor.stl", 0.079, (0.000037, 0.000025, 0.000021)),
        ("wrist_roll", f"Wrist_Roll_{suffix}", "0 -0.0601 0", "0 1.5708 0", "0 -1 0", -2.74385, 2.84121,
         "Fixed_Jaw.stl", "Fixed_Jaw_Motor.stl", 0.087, (0.000028, 0.000043, 0.000035)),
        ("gripper", f"Jaw_{suffix}", "-0.0202 -0.0244 0", "3.1416 0 3.33", "0 0 1", -0.37453, 1.74533,
         "Moving_Jaw.stl", None, 0.012, (0.0000066, 0.0000019, 0.0000053)),
    ]
    parent = base.attrib["name"]
    for key, joint_name, xyz, rpy, axis, lower, upper, visual, motor_visual, mass, inertia_diag in specs:
        child_name = f"{prefix}_{key}_link"
        link = ET.SubElement(robot, "link", name=child_name)
        inertial(link, mass, inertia=inertia_diag)
        mesh_visual(link, f"../assets/xlerobot/assets/{visual}")
        if motor_visual:
            mesh_visual(link, f"../assets/xlerobot/assets/{motor_visual}", mat="motor")
        primitive(link, "box", {"size": "0.07 0.07 0.10"}, collision=True)
        joint(
            robot,
            joint_name,
            "revolute",
            parent,
            child_name,
            xyz,
            rpy,
            axis,
            {"lower": lower, "upper": upper, "effort": 3.35 if key != "gripper" else 10, "velocity": 4.0},
        )
        parent = child_name


def build():
    robot = ET.Element("robot", name="xlerobot_v04_servo_dualwheel")
    for name, rgba in {
        "white": "0.82 0.82 0.82 1",
        "motor": "0.08 0.08 0.08 1",
        "blue": "0.08 0.18 0.55 1",
        "rubber": "0.03 0.03 0.03 1",
    }.items():
        material(robot, name, rgba)

    base = ET.SubElement(robot, "link", name="base_link")
    inertial(base, 10.0, "0 0 0", (0.70, 0.67, 0.30))
    mesh_visual(base, "../assets/xlerobot/assets/raskogbody.stl", "-0.01668 0.502 0.515", "1.5708 0 0", "0.0009 0.001 0.0009", "blue")
    mesh_visual(base, "../assets/xlerobot/v04/meshes/base_chassis.stl", "-0.15 0 -0.3065", "0 0 1.5708")
    mesh_visual(base, "../assets/xlerobot/v04/meshes/drive_side_a_mount.stl", "-0.15 0.205 -0.3065", "0 0 1.5708", mat="motor")
    mesh_visual(base, "../assets/xlerobot/v04/meshes/drive_side_b_mount.stl", "-0.15 -0.205 -0.3065", "0 0 1.5708", mat="motor")
    primitive(base, "box", {"size": "0.3913 0.459 0.10"}, "0 0 -0.30", collision=True)
    primitive(base, "box", {"size": "0.315 0.405 0.59"}, "0 0 0.015", collision=True)

    for side, y, rotor in (("left", 0.23, "a"), ("right", -0.23, "b")):
        link = ET.SubElement(robot, "link", name=f"{side}_wheel_link")
        inertial(link, 0.6, inertia=(0.0015, 0.0008, 0.0015))
        primitive(link, "cylinder", {"radius": "0.0635", "length": "0.04"}, rpy="1.5708 0 0", mat="rubber")
        primitive(link, "cylinder", {"radius": "0.0635", "length": "0.04"}, rpy="1.5708 0 0", collision=True)
        mesh_visual(link, f"../assets/xlerobot/v04/meshes/drive_side_{rotor}_rotor.stl", rpy="0 0 1.5708", mat="motor")
        joint(robot, f"{side}_wheel_joint", "continuous", "base_link", link.attrib["name"], f"-0.15 {y} -0.3065", axis="0 1 0", limits={"effort": 2.0, "velocity": 6.0})

    upper = ET.SubElement(robot, "link", name="upper_mount_link")
    inertial(upper, 0.75, inertia=(0.02, 0.02, 0.03))
    mesh_visual(upper, "../assets/xlerobot/v04/meshes/upper_arm_mount.stl", "-0.11436 0.0048 0.35352")
    joint(robot, "upper_mount_joint", "fixed", "base_link", "upper_mount_link")

    arm(robot, "left", "-0.09 -0.11 0.395", "0 0 0")
    arm(robot, "right", "-0.09 0.11 0.395", "0 0 3.14159265")

    neck = ET.SubElement(robot, "link", name="neck_base_link")
    inertial(neck, 0.35, inertia=(0.006, 0.006, 0.002))
    mesh_visual(neck, "../assets/xlerobot/v04/meshes/neck_refined.stl", "0 0 0.12152")
    joint(robot, "neck_mount_joint", "fixed", "base_link", "neck_base_link", "-0.09865 0.00474 0.42103")

    pan = ET.SubElement(robot, "link", name="head_pan_link")
    inertial(pan, 0.2556, inertia=(0.0129, 0.0095, 0.0184))
    mesh_visual(pan, "../assets/xlerobot/v04/meshes/head_gimbal_base.stl", "0 0 0.02985")
    mesh_visual(pan, "../assets/xlerobot/v04/meshes/head_yaw_housing.stl", "0.01144 -0.0001 0.07229", mat="motor")
    joint(robot, "head_pan_joint", "revolute", "neck_base_link", "head_pan_link", "-0.01409 0.00016 0.24267", axis="0 0 1", limits={"lower": -3.2, "upper": 3.2, "effort": 0.32, "velocity": 4.0})

    tilt = ET.SubElement(robot, "link", name="head_tilt_link")
    inertial(tilt, 0.10, inertia=(0.0061, 0.0014, 0.0061))
    mesh_visual(tilt, "../assets/xlerobot/v04/meshes/head_pitch_holder.stl")
    mesh_visual(tilt, "../assets/xlerobot/v04/meshes/camera_mount.stl", "0.025 0 0.03", "0 0 1.5708", mat="motor")
    primitive(tilt, "box", {"size": "0.020 0.070 0.054"}, "0.065 0 0.005", mat="motor")
    primitive(tilt, "cylinder", {"radius": "0.008", "length": "0.010"}, "0.078 0 0.005", "0 1.5708 0", mat="motor")
    joint(robot, "head_tilt_joint", "revolute", "head_pan_link", "head_tilt_link", "0.00258 -0.00072 0.09705", axis="0 1 0", limits={"lower": -0.76, "upper": 1.45, "effort": 0.68, "velocity": 4.0})

    camera = ET.SubElement(robot, "link", name="head_camera_optical_frame")
    inertial(camera, 0.02, inertia=(0.00001, 0.00001, 0.00001))
    joint(robot, "head_camera_joint", "fixed", "head_tilt_link", "head_camera_optical_frame", "0.083 0 0.005", "-1.5708 0 -1.5708")
    return robot


def main():
    root = build()
    rough = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(pretty, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
