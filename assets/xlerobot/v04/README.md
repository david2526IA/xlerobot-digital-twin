# Derived XLeRobot 0.4 meshes

These binary STL files are generated from the immutable official CAD snapshot
in `third_party/xlerobot_official`. Unlike conventional STL files whose unit is
implicit, every vertex in these derived files is numerically expressed in
**metres**.

Regenerate them on Windows with FreeCAD 1.1:

```powershell
& "C:\Program Files\FreeCAD 1.1\bin\python.exe" scripts\export_v04_meshes.py
.\.venv\Scripts\python.exe scripts\validate_v04_meshes.py
```

`mesh_manifest.json` records the source object labels, export-frame origins,
bounds, triangle counts and hashes. The source dual-wheel STEP is an exploded
presentation: its offsets are not valid assembled transforms. Drive-side A and
B therefore remain neutral names until the assembly transform is verified.

The drive mounts and moving rotors are not part of `base_chassis.stl`. This is
intentional: a wheel mesh fused into the chassis cannot rotate or generate
physical differential-drive contact.

The CAD circular component has a 60 mm bounding diameter. The official software
configuration uses a 50 mm effective wheel radius. This discrepancy remains
open for physical identification; neither value has been silently changed.
