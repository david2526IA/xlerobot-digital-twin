"""Evaluate a checkpoint produced by train_cem.py."""
from __future__ import annotations

import argparse
import numpy as np

from train_cem import features, rollout
from xlerobot_twin import XLeRobotReachEnv

parser = argparse.ArgumentParser()
parser.add_argument("checkpoint", nargs="?", default="outputs/models/cem_reach.npz")
parser.add_argument("--episodes", type=int, default=20)
args = parser.parse_args()
checkpoint = np.load(args.checkpoint)
weights = checkpoint["weights"]
horizon = int(checkpoint["horizon"]) if "horizon" in checkpoint.files else 300
env = XLeRobotReachEnv(domain_randomization=True, horizon=horizon)
results = [rollout(env, weights, 5000 + i, horizon) for i in range(args.episodes)]
print(f"episodes={args.episodes} mean_return={np.mean([r for r, _ in results]):.3f} success_rate={np.mean([s for _, s in results]):.2%}")
env.close()
