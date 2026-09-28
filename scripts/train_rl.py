"""Train PPO on the reach task; requires requirements-rl.txt."""

import argparse
import json
import platform
from pathlib import Path

import stable_baselines3
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env

from xlerobot_twin import XLeRobotReachEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timesteps", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-steps", type=int, default=1024)
    parser.add_argument("--n-envs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output", type=Path, default=Path("outputs/models/ppo_reach"))
    parser.add_argument("--tensorboard-log", type=Path)
    parser.add_argument("--resume", type=Path, help="Existing PPO .zip checkpoint")
    parser.add_argument("--checkpoint-freq", type=int, default=25_000)
    parser.add_argument("--device", default="auto", help="auto, cpu, cuda, ...")
    parser.add_argument("--action-mode", choices=("right_arm", "full"), default="right_arm")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.timesteps <= 0 or args.n_steps <= 1 or args.batch_size <= 1 or args.n_envs <= 0:
        raise SystemExit("timesteps, n-steps, n-envs and batch-size must be positive")
    if (args.n_steps * args.n_envs) % args.batch_size:
        raise SystemExit("n-steps * n-envs must be divisible by batch-size")

    env = make_vec_env(
        XLeRobotReachEnv,
        n_envs=args.n_envs,
        seed=args.seed,
        env_kwargs={"action_mode": args.action_mode},
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tensorboard_log = str(args.tensorboard_log) if args.tensorboard_log else None
    if args.resume:
        model = PPO.load(args.resume, env=env, device=args.device)
        model.tensorboard_log = tensorboard_log
    else:
        model = PPO(
            "MlpPolicy", env, verbose=1, seed=args.seed, device=args.device,
            n_steps=args.n_steps, batch_size=args.batch_size,
            tensorboard_log=tensorboard_log,
        )
    checkpoint_callback = None
    if args.checkpoint_freq > 0:
        checkpoint_dir = args.output.parent / f"{args.output.name}_checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_callback = CheckpointCallback(
            save_freq=args.checkpoint_freq,
            save_path=str(checkpoint_dir),
            name_prefix=args.output.name,
        )
    model.learn(
        total_timesteps=args.timesteps,
        callback=checkpoint_callback,
        reset_num_timesteps=not bool(args.resume),
    )
    model.save(args.output)
    manifest = {
        "algorithm": "PPO",
        "environment": "XLeRobotReachEnv",
        "action_mode": args.action_mode,
        "timesteps_this_run": args.timesteps,
        "seed": args.seed,
        "n_steps": args.n_steps,
        "n_envs": args.n_envs,
        "batch_size": args.batch_size,
        "resumed_from": str(args.resume) if args.resume else None,
        "stable_baselines3": stable_baselines3.__version__,
        "torch": torch.__version__,
        "python": platform.python_version(),
        "device": str(model.device),
    }
    args.output.with_suffix(".run.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    env.close()
    print(f"Saved PPO checkpoint to {args.output.with_suffix('.zip')}")


if __name__ == "__main__":
    main()
