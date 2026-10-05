from pathlib import Path

import mujoco
import numpy as np


MODEL = Path(__file__).resolve().parents[1] / "assets" / "xlerobot" / "xlerobot.xml"


def test_neutral_neck_camera_faces_operating_side():
    model = mujoco.MjModel.from_xml_path(str(MODEL))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    camera = model.camera("neck_rgb").id
    rotation = data.cam_xmat[camera].reshape(3, 3)
    view_direction = -rotation[:, 2]
    assert np.allclose(view_direction, [-1.0, 0.0, 0.0], atol=1e-6)
    assert data.cam_xpos[camera, 2] > 1.0


def test_table_and_camera_share_the_operating_side():
    model = mujoco.MjModel.from_xml_path(str(MODEL))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    table_x = data.xpos[model.body("training_table").id, 0]
    cube_x = data.xpos[model.body("target_cube").id, 0]
    camera = model.camera("neck_rgb").id
    view_direction = -data.cam_xmat[camera].reshape(3, 3)[:, 2]
    assert table_x < 0.0
    assert cube_x < 0.0
    assert view_direction[0] < -0.99
