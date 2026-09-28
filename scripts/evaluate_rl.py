"""Evaluate a Stable-Baselines3 PPO checkpoint in the reach environment."""

import argparse
import json
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO

from xlerobot_twin import XLeRobotReachEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1000)
    parser.add_argument("--min-success-rate", type=float, default=0.0)
    parser.add_argument("--json-output", type=Path)
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
    metrics = {
        "episodes": args.episodes,
        "mean_return": float(np.mean(returns)),
        "std_return": float(np.std(returns)),
        "success_rate": successes / args.episodes,
    }
    print(
        f"episodes={args.episodes} mean_return={metrics['mean_return']:.3f} "
        f"std_return={metrics['std_return']:.3f} success_rate={metrics['success_rate']:.1%}"
    )
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    if metrics["success_rate"] < args.min_success_rate:
        raise SystemExit(
            f"Policy rejected: success rate {metrics['success_rate']:.1%} "
            f"is below {args.min_success_rate:.1%}"
        )


if __name__ == "__main__":
    main()
