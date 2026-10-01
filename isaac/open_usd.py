"""Open the generated XLeRobot USD in a visible Isaac Sim window."""

from __future__ import annotations

import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("usd", type=Path)
args = parser.parse_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import omni.usd

usd_path = str(args.usd.resolve())
if not omni.usd.get_context().open_stage(usd_path):
    simulation_app.close()
    raise SystemExit(f"Could not open stage: {usd_path}")

while omni.usd.get_context().get_stage_loading_status()[2] > 0:
    simulation_app.update()

print(f"XLeRobot stage loaded: {usd_path}")
while simulation_app.is_running():
    simulation_app.update()
simulation_app.close()
