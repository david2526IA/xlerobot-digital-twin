from pathlib import Path

import mujoco
import numpy as np


MODEL = Path(__file__).resolve().parents[1] / "assets" / "xlerobot" / "xlerobot.xml"


def test_neutral_neck_camera_faces_robot_forward():
    model = mujoco.MjModel.from_xml_path(str(MODEL))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    camera = model.camera("neck_rgb").id
    rotation = data.cam_xmat[camera].reshape(3, 3)
    view_direction = -rotation[:, 2]
    assert np.allclose(view_direction, [1.0, 0.0, 0.0], atol=1e-6)
    assert data.cam_xpos[camera, 2] > 1.0
