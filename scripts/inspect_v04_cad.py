"""Inspect the official XLeRobot 0.4 STEP assemblies with FreeCADCmd.

Run with:
    "C:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe" scripts/inspect_v04_cad.py path.step
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import FreeCAD as App
import Import


def vector(value):
    return [round(value.x, 6), round(value.y, 6), round(value.z, 6)]


def center_of_mass(shape):
    """FreeCAD 1.1 exposes CenterOfGravity on compounds, CenterOfMass on solids."""
    value = getattr(shape, "CenterOfMass", None)
    if value is None:
        value = shape.CenterOfGravity
    return vector(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("assembly", type=Path)
    parser.add_argument("--all", action="store_true", help="include aggregate App::Part objects")
    args = parser.parse_args()

    source = args.assembly.resolve()
    document = App.newDocument("xlerobot_v04_audit")
    Import.insert(str(source), document.Name)
    document.recompute()

    records = []
    for obj in document.Objects:
        shape = getattr(obj, "Shape", None)
        if shape is None or shape.isNull() or not shape.Solids:
            continue
        if not args.all and obj.TypeId != "Part::Feature":
            continue
        records.append(
            {
                "name": obj.Name,
                "label": obj.Label,
                "type": obj.TypeId,
                "solids": len(shape.Solids),
                "volume_mm3": round(shape.Volume, 3),
                "center_of_mass_mm": center_of_mass(shape),
                "bound_box_mm": {
                    "min": [
                        round(shape.BoundBox.XMin, 6),
                        round(shape.BoundBox.YMin, 6),
                        round(shape.BoundBox.ZMin, 6),
                    ],
                    "max": [
                        round(shape.BoundBox.XMax, 6),
                        round(shape.BoundBox.YMax, 6),
                        round(shape.BoundBox.ZMax, 6),
                    ],
                },
            }
        )

    print(json.dumps({"source": str(source), "objects": records}, indent=2))


if __name__ == "__main__":
    main()
