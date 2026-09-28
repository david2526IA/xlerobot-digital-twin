import numpy as np
import mujoco
from gymnasium.utils.env_checker import check_env

from xlerobot_twin import XLeRobotReachEnv


def test_gym_api_and_deterministic_reset():
    env = XLeRobotReachEnv(domain_randomization=False, horizon=2)
    check_env(env, skip_render_check=True)
    obs_a, _ = env.reset(seed=123)
    obs_b, _ = env.reset(seed=123)
    np.testing.assert_allclose(obs_a, obs_b)
    _, reward, terminated, truncated, info = env.step(np.zeros(16, dtype=np.float32))
    assert np.isfinite(reward)
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    assert "success" in info
    env.close()


def test_cube_settles_on_table_surface():
    env = XLeRobotReachEnv(domain_randomization=False)
    env.reset(seed=5)
    for _ in range(500):
        mujoco.mj_step(env.model, env.data)
    cube_z = env.data.xpos[env.model.body("target_cube").id, 2]
    # Table surface 0.775 m + cube half-height 0.0225 m.
    assert 0.792 < cube_z < 0.803, cube_z
    env.close()


def test_reach_targets_are_inside_table_edge_workspace():
    env = XLeRobotReachEnv(domain_randomization=False)
    for seed in range(20):
        observation, _ = env.reset(seed=seed)
        cube = observation[-9:-6]
        assert 0.18 <= cube[0] <= 0.30
        assert -0.15 <= cube[1] <= 0.15
    env.close()
