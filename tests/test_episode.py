import numpy as np
import pytest

from xlerobot_twin.episode import ACTION_NAMES, EpisodeRecorder


def test_episode_contract_is_time_aligned_and_explicit():
    recorder = EpisodeRecorder(control_dt_s=0.04, source="test")
    for step in range(2):
        recorder.append(
            observation=np.full(3, step),
            action=np.zeros(len(ACTION_NAMES)),
            reward=float(step),
            qpos=np.full(2, step),
            qvel=np.full(2, step),
            image=np.zeros((2, 2, 3), dtype=np.uint8),
        )
    payload = recorder.payload(task="test_task", success=True)

    assert payload["schema_version"] == "xlerobot_episode_v1"
    assert tuple(payload["action_names"]) == ACTION_NAMES
    np.testing.assert_allclose(payload["timestamp_s"], [0.0, 0.04])
    assert payload["action"].shape == (2, len(ACTION_NAMES))
    assert payload["neck_rgb"].shape == (2, 2, 2, 3)
    assert bool(payload["success"])


def test_episode_contract_rejects_wrong_action_dimension():
    recorder = EpisodeRecorder(control_dt_s=0.04, source="test")
    with pytest.raises(ValueError, match="Expected"):
        recorder.append(
            observation=np.zeros(1),
            action=np.zeros(3),
            reward=0,
            qpos=np.zeros(1),
            qvel=np.zeros(1),
        )
