"""Add the simulated neck RGB/depth cameras to an imported XLeRobot v0.4 USD."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from pxr import Gf, Usd, UsdGeom


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("usd", type=Path)
    args = parser.parse_args()
    path = args.usd.resolve()
    stage = Usd.Stage.Open(str(path))
    if stage is None:
        raise SystemExit(f"Could not open USD: {path}")

    frame = next((prim for prim in stage.Traverse() if prim.GetName() == "head_camera_optical_frame"), None)
    if frame is None:
        raise SystemExit("Imported USD has no head_camera_optical_frame")

    horizontal_aperture_mm = 20.955
    vertical_aperture_mm = horizontal_aperture_mm * 9.0 / 16.0
    focal_length_mm = horizontal_aperture_mm / (2.0 * math.tan(math.radians(60.0) / 2.0))
    for name in ("neck_rgb", "neck_depth"):
        camera = UsdGeom.Camera.Define(stage, frame.GetPath().AppendChild(name))
        camera.CreateFocalLengthAttr(focal_length_mm)
        camera.CreateHorizontalApertureAttr(horizontal_aperture_mm)
        camera.CreateVerticalApertureAttr(vertical_aperture_mm)
        camera.CreateClippingRangeAttr(Gf.Vec2f(0.03, 100.0))
        xform = UsdGeom.Xformable(camera.GetPrim())
        rotate = next((op for op in xform.GetOrderedXformOps() if op.GetOpName() == "xformOp:rotateY"), None)
        (rotate or xform.AddRotateYOp()).Set(180.0)
        camera.GetPrim().SetCustomDataByKey("xlerobot:sensor_role", "rgb" if name == "neck_rgb" else "depth")
        camera.GetPrim().SetCustomDataByKey("xlerobot:calibration", "provisional_60deg_fov")

    stage.GetRootLayer().Save()
    print(f"PASS: added neck_rgb and neck_depth below {frame.GetPath()}")


if __name__ == "__main__":
    main()
