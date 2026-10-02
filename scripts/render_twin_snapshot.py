"""Render a reproducible overview image of the current MuJoCo twin."""
from pathlib import Path

import mujoco
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "assets" / "xlerobot" / "xlerobot.xml"
OUTPUT_DIR = ROOT / "outputs"

model = mujoco.MjModel.from_xml_path(str(MODEL))
data = mujoco.MjData(model)
mujoco.mj_forward(model, data)

shots = {
    "xlerobot_v04_overview.png": ([0.0, 0.0, 0.72], 2.25, 135, -18),
    "xlerobot_v04_front.png": ([-0.10, 0.0, 0.20], 0.95, 0, -8),
    "xlerobot_v04_head.png": ([-0.10, 0.0, 0.94], 0.52, 180, -3),
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
with mujoco.Renderer(model, height=480, width=640) as renderer:
    for filename, (lookat, distance, azimuth, elevation) in shots.items():
        camera = mujoco.MjvCamera()
        camera.type = mujoco.mjtCamera.mjCAMERA_FREE
        camera.lookat[:] = lookat
        camera.distance = distance
        camera.azimuth = azimuth
        camera.elevation = elevation
        renderer.update_scene(data, camera=camera)
        output = OUTPUT_DIR / filename
        Image.fromarray(renderer.render()).save(output)
        print(output)
