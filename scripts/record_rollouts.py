"""Record simulated episodes in a transparent NPZ interchange format."""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
from xlerobot_twin import XLeRobotReachEnv

parser = argparse.ArgumentParser()
parser.add_argument("--episodes", type=int, default=10)
parser.add_argument("--output", default="datasets/raw/reach_random")
parser.add_argument("--images", action="store_true", help="Store neck_rgb frames for VLA datasets")
parser.add_argument("--seed", type=int, default=0)
args = parser.parse_args()
output = Path(args.output); output.mkdir(parents=True, exist_ok=True)
env = XLeRobotReachEnv(render_mode="rgb_array" if args.images else None, domain_randomization=True)
for episode in range(args.episodes):
    obs, _ = env.reset(seed=args.seed + episode)
    observations, actions, rewards, images = [], [], [], []
    for _ in range(env.horizon):
        action = env.action_space.sample()
        observations.append(obs); actions.append(action)
        if args.images:
            images.append(env.render())
        obs, reward, terminated, truncated, _ = env.step(action)
        rewards.append(reward)
        if terminated or truncated:
            break
    payload = {"observation": np.asarray(observations), "action": np.asarray(actions), "reward": np.asarray(rewards), "task": "reach the cube"}
    if args.images:
        payload["neck_rgb"] = np.asarray(images, dtype=np.uint8)
    np.savez_compressed(output / f"episode_{episode:05d}.npz", **payload)
print(f"Wrote {args.episodes} episodes to {output}")
env.close()
