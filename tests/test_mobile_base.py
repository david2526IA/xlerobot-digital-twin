import math
from pathlib import Path

import mujoco
import numpy as np


MODEL = Path(__file__).resolve().parents[1] / "assets" / "xlerobot" / "xlerobot.xml"


def load_settled():
    model = mujoco.MjModel.from_xml_path(str(MODEL))
    data = mujoco.MjData(model)
    for _ in range(1000):
        mujoco.mj_step(model, data)
    return model, data


def test_differential_base_moves_forward_and_turns():
    model, data = load_settled()
    start_x = data.qpos[0]
    data.ctrl[model.actuator("forward").id] = 0.7
    for _ in range(3000):
        mujoco.mj_step(model, data)
    assert np.isfinite(data.qpos).all()
    assert data.qpos[0] - start_x > 0.05

    model, data = load_settled()
    data.ctrl[model.actuator("turn").id] = 0.7
    for _ in range(3000):
        mujoco.mj_step(model, data)
    w, x, y, z = data.qpos[3:7]
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    assert np.isfinite(data.qpos).all()
    assert abs(yaw) > 0.3
