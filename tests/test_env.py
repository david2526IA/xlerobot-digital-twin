import numpy as np
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
