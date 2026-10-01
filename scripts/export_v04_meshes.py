"""Export separated, metre-scale meshes from the pinned XLeRobot 0.4 STEP CAD.

This script must run with FreeCAD's bundled Python, for example:

    & "C:\\Program Files\\FreeCAD 1.1\\bin\\python.exe" scripts/export_v04_meshes.py

The upstream dual-wheel STEP is an exploded presentation assembly. Each drive
component is therefore exported in its own local frame; the source presentation
offsets are recorded but are never interpreted as assembled joint transforms.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

import FreeCAD as App
import Import


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "third_party" / "xlerobot_official" / "hardware" / "step" / "XLeRobot_040"
OUTPUT_ROOT = ROOT / "assets" / "xlerobot" / "v04"
MESH_ROOT = OUTPUT_ROOT / "meshes"

ASSEMBLIES = {
    "dualwheelbase": {
        "source": "XLeRobot040_dualwheelbase.step",
        "exports": {
            "base_chassis": {
                "objects": ["Part__Feature", "Part__Feature001", "Part__Feature006", "Part__Feature007"],
                "role": "static",
                "notes": "Rigid central support; drive components deliberately excluded.",
            },
            "drive_side_a_mount": {
                "objects": ["Part__Feature002"],
                "role": "drive_interface",
                "notes": "Exploded CAD component; side assignment is deferred to assembly.",
            },
            "drive_side_b_mount": {
                "objects": ["Part__Feature003"],
                "role": "drive_interface",
                "notes": "Exploded CAD component; side assignment is deferred to assembly.",
            },
            "drive_side_a_rotor": {
                "objects": ["Part__Feature004"],
                "role": "moving_wheel",
                "notes": "Kept separate from chassis and mount so it can rotate physically.",
            },
            "drive_side_b_rotor": {
                "objects": ["Part__Feature005"],
                "role": "moving_wheel",
                "notes": "Kept separate from chassis and mount so it can rotate physically.",
            },
        },
    },
    "armbase": {
        "source": "XLeRobot040_armbase.step",
        "exports": {
            "soft_gripper_body": {"objects": ["Part__Feature"], "role": "optional_gripper"},
            "soft_gripper_servo_mount": {"objects": ["Part__Feature001"], "role": "optional_gripper"},
            "soft_gripper_finger_a": {"objects": ["Part__Feature002"], "role": "optional_gripper_moving"},
            "soft_gripper_finger_b": {"objects": ["Part__Feature003"], "role": "optional_gripper_moving"},
            "head_yaw_housing": {"objects": ["Part__Feature004"], "role": "head_pan"},
            "neck_column_reference": {
                "objects": ["Part__Feature005"],
                "role": "superseded_reference",
                "notes": "Preserved for comparison; neck_refined is the selected v0.4 column.",
            },
            "head_gimbal_base": {"objects": ["Part__Feature006"], "role": "head_pan"},
            "head_pitch_holder": {"objects": ["Part__Feature007"], "role": "head_tilt"},
            "camera_mount": {"objects": ["Part__Feature008"], "role": "head_tilt"},
            "upper_arm_mount": {
                "objects": [
                    "Part__Feature009",
                    "Part__Feature010",
                    "Part__Feature011",
                    "Part__Feature012",
                    "Part__Feature013",
                ],
                "role": "static",
                "notes": "Rigid modular upper base for the two SO-101 arms and centre support.",
            },
        },
    },
    "neck": {
        "source": "XLeRobot040_neck_refined.step",
        "exports": {
            "neck_refined": {
                "objects": ["Part__Feature"],
                "role": "static",
                "notes": "Selected refined v0.4 neck column.",
            }
        },
    },
}


def union_bounds(objects):
    boxes = [obj.Shape.BoundBox for obj in objects]
    return {
        "min": [min(getattr(box, axis + "Min") for box in boxes) for axis in "XYZ"],
        "max": [max(getattr(box, axis + "Max") for box in boxes) for axis in "XYZ"],
    }


def midpoint(bounds):
    return [(lo + hi) / 2.0 for lo, hi in zip(bounds["min"], bounds["max"])]


def transform(point, origin_mm):
    # STEP coordinates are retained; only translation and mm -> m are applied.
    return tuple((coordinate - origin) * 0.001 for coordinate, origin in zip(point, origin_mm))


def normal(a, b, c):
    ux, uy, uz = (b[i] - a[i] for i in range(3))
    vx, vy, vz = (c[i] - a[i] for i in range(3))
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (0.0, 0.0, 0.0) if length == 0 else (nx / length, ny / length, nz / length)


def write_binary_stl(path, name, objects, origin_mm):
    triangles_out = []
    for obj in objects:
        vertices, triangles = obj.Shape.tessellate(0.35)
        points = [transform((v.x, v.y, v.z), origin_mm) for v in vertices]
        triangles_out.extend(tuple(points[index] for index in tri) for tri in triangles)

    minima = [float("inf")] * 3
    maxima = [float("-inf")] * 3
    with path.open("wb") as stream:
        header = f"XLeRobot v0.4 {name} | metres".encode("ascii")[:80]
        stream.write(header.ljust(80, b"\0"))
        stream.write(struct.pack("<I", len(triangles_out)))
        for a, b, c in triangles_out:
            nx, ny, nz = normal(a, b, c)
            stream.write(struct.pack("<12fH", nx, ny, nz, *a, *b, *c, 0))
            for vertex in (a, b, c):
                for axis, coordinate in enumerate(vertex):
                    minima[axis] = min(minima[axis], coordinate)
                    maxima[axis] = max(maxima[axis], coordinate)
    return len(triangles_out), [maxima[i] - minima[i] for i in range(3)]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    MESH_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "units": "metre",
        "mesh_frame": "source STEP axes, centred at the recorded source_origin_mm",
        "assembly_warning": (
            "The dual-wheel STEP is exploded. source_origin_mm is an export frame, "
            "not an assembled joint transform."
        ),
        "meshes": [],
    }

    for assembly_name, assembly in ASSEMBLIES.items():
        source = SOURCE_ROOT / assembly["source"]
        document = App.newDocument(f"xlerobot_{assembly_name}")
        Import.insert(str(source), document.Name)
        document.recompute()
        by_name = {obj.Name: obj for obj in document.Objects}

        for export_name, config in assembly["exports"].items():
            missing = [name for name in config["objects"] if name not in by_name]
            if missing:
                raise RuntimeError(f"{source.name}: missing objects {missing}")
            objects = [by_name[name] for name in config["objects"]]
            bounds = union_bounds(objects)
            origin_mm = midpoint(bounds)
            output = MESH_ROOT / f"{export_name}.stl"
            triangle_count, local_size_m = write_binary_stl(output, export_name, objects, origin_mm)
            cad_size_m = [(hi - lo) * 0.001 for lo, hi in zip(bounds["min"], bounds["max"])]
            manifest["meshes"].append(
                {
                    "name": export_name,
                    "file": output.relative_to(ROOT).as_posix(),
                    "source": source.relative_to(ROOT).as_posix(),
                    "source_objects": [
                        {"name": obj.Name, "label": obj.Label} for obj in objects
                    ],
                    "role": config["role"],
                    "notes": config.get("notes", ""),
                    "source_origin_mm": [round(value, 6) for value in origin_mm],
                    "source_bounds_mm": {
                        key: [round(value, 6) for value in values]
                        for key, values in bounds.items()
                    },
                    "local_size_m": [round(value, 9) for value in local_size_m],
                    "cad_size_m": [round(value, 9) for value in cad_size_m],
                    "cad_volume_mm3": round(sum(obj.Shape.Volume for obj in objects), 3),
                    "triangle_count": triangle_count,
                    "sha256": sha256(output),
                }
            )
        App.closeDocument(document.Name)

    manifest_path = OUTPUT_ROOT / "mesh_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: exported {len(manifest['meshes'])} separated metre-scale meshes")
    print(manifest_path)


if __name__ == "__main__":
    main()
