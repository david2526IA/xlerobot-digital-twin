# Canonical XLeRobot 0.4 robot description

`xlerobot_v04.urdf` is the canonical simulator-neutral description assembled
from the pinned XLeRobot 0.4 CAD, the official two-wheel controller values and
the existing SO-101 kinematic reference.

Regenerate and validate it with:

```powershell
.\.venv\Scripts\python.exe scripts\generate_v04_urdf.py
.\.venv\Scripts\python.exe scripts\validate_v04_description.py
```

The description has 22 links, 21 joints and 16 moving joints: two wheels, twelve
arm/gripper joints and two head joints. The two 127 mm directional wheels are
continuous revolute joints at a 0.25 m track. The physical tire radius is
0.0635 m; the official controller's separate effective conversion radius is
0.05 m and is retained in `twin/manifest.yaml`.

The CAD dual-wheel assembly is exploded, so longitudinal/vertical mounting
offsets not recoverable from published evidence are provisional. They are
centralized in the generator and frame manifest rather than hidden in manually
edited simulator files.
