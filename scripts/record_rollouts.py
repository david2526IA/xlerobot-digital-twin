"""Record simulated episodes in a transparent NPZ interchange format."""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
from xlerobot_twin import XLeRobotReachEnv

parser = argparse.ArgumentParser()
parser.add_argument("--episodes", type=int, default=10)
parser.add_argument("--output", default="datasets/raw/reach_random")
args = parser.parse_args()
output = Path(args.output); output.mkdir(parents=True, exist_ok=True)
env = XLeRobotReachEnv(domain_randomization=True)
for episode in range(args.episodes):
    obs, _ = env.reset(seed=episode)
    observations, actions, rewards = [], [], []
    for _ in range(env.horizon):
        action = env.action_space.sample()
        observations.append(obs); actions.append(action)
        obs, reward, terminated, truncated, _ = env.step(action)
        rewards.append(reward)
        if terminated or truncated:
            break
    np.savez_compressed(output / f"episode_{episode:05d}.npz", observation=np.asarray(observations), action=np.asarray(actions), reward=np.asarray(rewards), task="reach the cube")
print(f"Wrote {args.episodes} episodes to {output}")
