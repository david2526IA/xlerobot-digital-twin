"""Evaluate a Stable-Baselines3 PPO checkpoint in the reach environment."""

import argparse
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO

from xlerobot_twin import XLeRobotReachEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env = XLeRobotReachEnv()
    model = PPO.load(args.checkpoint, env=env)
    returns: list[float] = []
    successes = 0
    for episode in range(args.episodes):
        observation, _ = env.reset(seed=args.seed + episode)
        episode_return = 0.0
        terminated = truncated = False
        while not (terminated or truncated):
            action, _ = model.predict(observation, deterministic=True)
            observation, reward, terminated, truncated, info = env.step(action)
            episode_return += float(reward)
        returns.append(episode_return)
        successes += int(bool(info.get("success", False)))
    env.close()
    print(
        f"episodes={args.episodes} mean_return={np.mean(returns):.3f} "
        f"std_return={np.std(returns):.3f} success_rate={successes / args.episodes:.1%}"
    )


if __name__ == "__main__":
    main()
