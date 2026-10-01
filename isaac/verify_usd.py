"""Verify the USD generated from the canonical XLeRobot v0.4 URDF."""

from __future__ import annotations

import argparse
from pathlib import Path

from pxr import Usd, UsdGeom, UsdPhysics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("usd", type=Path)
    args = parser.parse_args()
    stage = Usd.Stage.Open(str(args.usd.resolve()))
    if stage is None:
        raise SystemExit(f"Could not open USD: {args.usd}")
    names = {prim.GetName() for prim in stage.Traverse()}
    required = {
        "left_wheel_joint", "right_wheel_joint",
        "Rotation_L", "Pitch_L", "Elbow_L", "Wrist_Pitch_L", "Wrist_Roll_L", "Jaw_L",
        "Rotation_R", "Pitch_R", "Elbow_R", "Wrist_Pitch_R", "Wrist_Roll_R", "Jaw_R",
        "head_pan_joint", "head_tilt_joint",
    }
    missing = required - names
    if missing:
        raise SystemExit(f"Imported USD is missing joints/prims: {sorted(missing)}")
    joints = [prim for prim in stage.Traverse() if prim.IsA(UsdPhysics.RevoluteJoint)]
    cameras = [prim.GetName() for prim in stage.Traverse() if prim.IsA(UsdGeom.Camera)]
    missing_cameras = {"neck_rgb", "neck_depth"} - set(cameras)
    if missing_cameras:
        raise SystemExit(f"Imported USD is missing cameras: {sorted(missing_cameras)}")
    print(f"PASS: USD={args.usd} revolute_joints={len(joints)} cameras={cameras}")


if __name__ == "__main__":
    main()
