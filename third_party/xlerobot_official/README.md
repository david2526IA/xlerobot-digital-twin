# XLeRobot official CAD snapshot

This directory contains an unmodified snapshot of the CAD inputs required to
reconstruct the XLeRobot 0.4 servo dual-wheel embodiment. The files come from
[Vector-Wangel/XLeRobot](https://github.com/Vector-Wangel/XLeRobot) at commit
`749abc837d5d771f26aeff961009c290e574b024`.

The upstream Apache-2.0 license is preserved in `LICENSE`. `SOURCE.yaml` records
the original paths and SHA-256 hashes. Do not edit these source files in place;
derived simulation meshes belong under `assets/xlerobot/v04/` and must be
regenerable.

Verify the snapshot from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\verify_official_assets.py
```

Inspect a STEP assembly with the FreeCAD Python runtime:

```powershell
& "C:\Program Files\FreeCAD 1.1\bin\python.exe" scripts\inspect_v04_cad.py `
  third_party\xlerobot_official\hardware\step\XLeRobot_040\XLeRobot040_dualwheelbase.step
```
