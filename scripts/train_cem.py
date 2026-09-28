"""Dependency-light CEM trainer for end-to-end environment verification.

This is intentionally a small baseline, not the final manipulation policy. It proves
that reset -> rollout -> reward -> optimization -> checkpoint -> evaluation works
without requiring PyTorch.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from xlerobot_twin import XLeRobotReachEnv


def features(obs: np.ndarray) -> np.ndarray:
    cube, left, right = obs[-9:-6], obs[-6:-3], obs[-3:]
    return np.concatenate((cube - left, cube - right, [1.0])).astype(np.float32)


def rollout(env: XLeRobotReachEnv, weights: np.ndarray, seed: int, horizon: int) -> tuple[float, bool]:
    obs, _ = env.reset(seed=seed)
    total = 0.0
    success = False
    for _ in range(horizon):
        action = np.tanh(weights @ features(obs))
        obs, reward, terminated, truncated, info = env.step(action)
        total += reward
        success = bool(info["success"])
        if terminated or truncated:
            break
    return total, success


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=40)
    parser.add_argument("--population", type=int, default=32)
    parser.add_argument("--elite", type=int, default=8)
    parser.add_argument("--horizon", type=int, default=150)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="outputs/models/cem_reach.npz")
    args = parser.parse_args()
    if not 1 <= args.elite <= args.population:
        raise SystemExit("--elite must be between 1 and --population")

    rng = np.random.default_rng(args.seed)
    mean = np.zeros((16, 7), dtype=np.float32)
    std = np.full_like(mean, 0.35)
    env = XLeRobotReachEnv(domain_randomization=True, horizon=args.horizon)
    history: list[dict[str, float]] = []
    best_weights, best_score = mean.copy(), -np.inf
    for iteration in range(args.iterations):
        population = rng.normal(mean, std, size=(args.population, *mean.shape)).astype(np.float32)
        scores = np.asarray([rollout(env, w, args.seed + iteration, args.horizon)[0] for w in population])
        elite = population[np.argsort(scores)[-args.elite:]]
        mean, std = elite.mean(axis=0), np.maximum(elite.std(axis=0), 0.03)
        if scores.max() > best_score:
            best_score = float(scores.max())
            best_weights = population[int(scores.argmax())].copy()
        record = {"iteration": iteration + 1, "mean_return": float(scores.mean()), "best_return": best_score}
        history.append(record)
        print(json.dumps(record))

    eval_returns, successes = zip(*(rollout(env, best_weights, 1000 + i, args.horizon) for i in range(10)))
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(target, weights=best_weights, feature_version=1, horizon=args.horizon)
    metrics = {"mean_return": float(np.mean(eval_returns)), "success_rate": float(np.mean(successes)), "history": history}
    target.with_suffix(".json").write_text(json.dumps(metrics, indent=2))
    print(f"saved={target} eval={metrics['mean_return']:.3f} success={metrics['success_rate']:.2%}")
    env.close()


if __name__ == "__main__":
    main()
