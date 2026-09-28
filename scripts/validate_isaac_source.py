"""Preflight the MJCF package before importing it into Isaac Sim."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
model_path = ROOT / "assets" / "xlerobot" / "xlerobot.xml"
root = ET.parse(model_path).getroot()
compiler = root.find("compiler")
mesh_dir = model_path.parent / (compiler.get("meshdir", ".") if compiler is not None else ".")
missing = []
for mesh in root.findall("./asset/mesh"):
    file_name = mesh.get("file")
    if file_name and not (mesh_dir / file_name).resolve().is_file():
        missing.append(file_name)
if missing:
    raise SystemExit(f"Missing MJCF meshes: {missing}")
required = {"neck_rgb", "neck_depth"}
cameras = {camera.get("name") for camera in root.findall(".//camera")}
if not required <= cameras:
    raise SystemExit(f"Missing cameras: {sorted(required - cameras)}")
actuators = root.find("actuator")
if actuators is None or len(actuators) != 16:
    raise SystemExit(f"Expected 16 actuators, found {0 if actuators is None else len(actuators)}")
print(f"PASS: Isaac MJCF source | meshes={len(root.findall('./asset/mesh'))} cameras={sorted(required)} actuators=16")
