"""Train PPO on the reach task; requires requirements-rl.txt."""

import argparse
from pathlib import Path

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

from xlerobot_twin import XLeRobotReachEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timesteps", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-steps", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output", type=Path, default=Path("outputs/models/ppo_reach"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.timesteps <= 0 or args.n_steps <= 1 or args.batch_size <= 1:
        raise SystemExit("timesteps, n-steps and batch-size must be positive")
    if args.n_steps % args.batch_size:
        raise SystemExit("n-steps must be divisible by batch-size for this single-environment trainer")

    env = make_vec_env(XLeRobotReachEnv, n_envs=1, seed=args.seed)
    model = PPO(
        "MlpPolicy", env, verbose=1, seed=args.seed,
        n_steps=args.n_steps, batch_size=args.batch_size,
        tensorboard_log="outputs/tensorboard",
    )
    model.learn(total_timesteps=args.timesteps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    model.save(args.output)
    env.close()
    print(f"Saved PPO checkpoint to {args.output.with_suffix('.zip')}")


if __name__ == "__main__":
    main()
