"""Validate generated XLeRobot 0.4 binary STL meshes and their separation."""
from __future__ import annotations

import hashlib
import json
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "xlerobot" / "v04" / "mesh_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def binary_stl_bounds(path: Path):
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError("file is shorter than a binary STL header")
    count = struct.unpack_from("<I", data, 80)[0]
    expected_size = 84 + count * 50
    if len(data) != expected_size:
        raise ValueError(f"size={len(data)} expected={expected_size}")
    minima = [float("inf")] * 3
    maxima = [float("-inf")] * 3
    for offset in range(84, len(data), 50):
        values = struct.unpack_from("<12fH", data, offset)
        for vertex in (values[3:6], values[6:9], values[9:12]):
            for axis, coordinate in enumerate(vertex):
                minima[axis] = min(minima[axis], coordinate)
                maxima[axis] = max(maxima[axis], coordinate)
    return count, [maxima[i] - minima[i] for i in range(3)]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    names = {record["name"] for record in manifest["meshes"]}
    required = {
        "base_chassis",
        "drive_side_a_mount",
        "drive_side_b_mount",
        "drive_side_a_rotor",
        "drive_side_b_rotor",
        "upper_arm_mount",
        "neck_refined",
    }
    if missing := required - names:
        errors.append(f"missing required meshes: {sorted(missing)}")

    moving = [record for record in manifest["meshes"] if record["role"] == "moving_wheel"]
    if len(moving) != 2:
        errors.append(f"expected 2 moving wheel meshes, found {len(moving)}")

    chassis = next(record for record in manifest["meshes"] if record["name"] == "base_chassis")
    chassis_objects = {entry["name"] for entry in chassis["source_objects"]}
    wheel_objects = {
        entry["name"]
        for record in moving
        for entry in record["source_objects"]
    }
    if chassis_objects & wheel_objects:
        errors.append("moving wheel geometry was fused into base_chassis")

    for record in manifest["meshes"]:
        path = ROOT / record["file"]
        if not path.is_file():
            errors.append(f"missing mesh: {record['file']}")
            continue
        if sha256(path) != record["sha256"]:
            errors.append(f"hash mismatch: {record['file']}")
            continue
        try:
            triangle_count, size = binary_stl_bounds(path)
        except ValueError as exc:
            errors.append(f"invalid binary STL {record['file']}: {exc}")
            continue
        if triangle_count != record["triangle_count"]:
            errors.append(f"triangle mismatch: {record['file']}")
        expected = record["local_size_m"]
        if any(abs(a - b) > 1e-5 for a, b in zip(size, expected)):
            errors.append(f"metre-scale bounds mismatch: {record['file']} {size} != {expected}")
        if max(size) > 1.0:
            errors.append(f"implausible metre-scale mesh: {record['file']} size={size}")

    if not errors:
        root = ET.Element("mujoco", model="xlerobot_v04_mesh_validation")
        assets = ET.SubElement(root, "asset")
        worldbody = ET.SubElement(root, "worldbody")
        body = ET.SubElement(worldbody, "body", name="mesh_grid")
        for index, record in enumerate(manifest["meshes"]):
            mesh_name = f"mesh_{index}"
            ET.SubElement(
                assets,
                "mesh",
                name=mesh_name,
                file=(ROOT / record["file"]).as_posix(),
            )
            ET.SubElement(
                body,
                "geom",
                type="mesh",
                mesh=mesh_name,
                pos=f"{(index % 4) * 0.4} {(index // 4) * 0.4} 0",
            )
        try:
            model = mujoco.MjModel.from_xml_string(ET.tostring(root, encoding="unicode"))
            if model.nmesh != len(manifest["meshes"]):
                errors.append(f"MuJoCo loaded {model.nmesh} of {len(manifest['meshes'])} meshes")
        except Exception as exc:
            errors.append(f"MuJoCo could not load generated meshes: {exc}")

    if errors:
        raise SystemExit("v0.4 mesh validation failed:\n" + "\n".join(errors))
    print(
        f"PASS: {len(manifest['meshes'])} v0.4 meshes in metres | "
        f"moving_wheels={len(moving)} | chassis_separated=true"
    )


if __name__ == "__main__":
    main()
