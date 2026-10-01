"""Render a reproducible overview image of the current MuJoCo twin."""
from pathlib import Path

import mujoco
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "assets" / "xlerobot" / "xlerobot.xml"
OUTPUT = ROOT / "outputs" / "xlerobot_v04_overview.png"

model = mujoco.MjModel.from_xml_path(str(MODEL))
data = mujoco.MjData(model)
mujoco.mj_forward(model, data)

camera = mujoco.MjvCamera()
camera.type = mujoco.mjtCamera.mjCAMERA_FREE
camera.lookat[:] = [0.0, 0.0, 0.72]
camera.distance = 2.25
camera.azimuth = 135
camera.elevation = -18

with mujoco.Renderer(model, height=480, width=640) as renderer:
    renderer.update_scene(data, camera=camera)
    pixels = renderer.render()

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
Image.fromarray(pixels).save(OUTPUT)
print(OUTPUT)
