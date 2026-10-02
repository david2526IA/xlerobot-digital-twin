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
continuous revolute joints at a provisional 0.50 m physical track, placing the
50 mm wide tires outside the 0.459 m cart envelope. The physical tire radius is
0.0635 m. The official controller's 0.05 m effective
radius and 0.25 m effective `wheelbase` remain separate in `twin/manifest.yaml`.

The CAD dual-wheel assembly is exploded, so longitudinal/vertical mounting
offsets not recoverable from published evidence are provisional. They are
centralized in the generator and frame manifest rather than hidden in manually
edited simulator files.
