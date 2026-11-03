"""Run the configured simulation-only nominal or randomized PPO protocol."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/sim2real_baseline.yaml")
    parser.add_argument("--condition", choices=("nominal", "randomized"), required=True)
    parser.add_argument("--timesteps", type=int, help="Override configured timesteps for a smoke run")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/sim2real")
    return parser.parse_args()


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    if config["hardware_gate"]["allowed"]:
        raise SystemExit("This runner is simulation-only; hardware_gate.allowed must remain false")
    condition = config["domains"][args.condition]
    training = config["training"]
    task = config["task"]
    evaluation = config["evaluation"]
    timesteps = args.timesteps or training["timesteps"]
    if timesteps <= 0:
        raise SystemExit("timesteps must be positive")

    run_dir = args.output_dir / args.condition
    run_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for seed in config["experiment"]["train_seeds"]:
        checkpoint = run_dir / f"ppo_seed_{seed}"
        train = [
            sys.executable, "scripts/train_rl.py", "--timesteps", str(timesteps),
            "--seed", str(seed), "--n-steps", str(training["n_steps"]),
            "--n-envs", str(training["n_envs"]), "--batch-size", str(training["batch_size"]),
            "--device", str(training["device"]), "--action-mode", task["action_mode"],
            "--output", str(checkpoint),
        ]
        if not condition["domain_randomization"]:
            train.append("--no-domain-randomization")
        run(train)
        evaluations = []
        for evaluation_seed in config["experiment"]["evaluation_seeds"]:
            metrics = checkpoint.with_suffix(f".eval_seed_{evaluation_seed}.metrics.json")
            evaluate = [
                sys.executable, "scripts/evaluate_rl.py", str(checkpoint.with_suffix(".zip")),
                "--episodes", str(evaluation["episodes_per_seed"]),
                "--seed", str(evaluation_seed), "--action-mode", task["action_mode"],
                "--json-output", str(metrics),
            ]
            if not condition["domain_randomization"]:
                evaluate.append("--no-domain-randomization")
            run(evaluate)
            evaluations.append(json.loads(metrics.read_text(encoding="utf-8")))
        records.append({"train_seed": seed, "evaluations": evaluations})

    summary = {
        "condition": args.condition,
        "simulation_only": True,
        "config": str(args.config),
        "timesteps": timesteps,
        "runs": records,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Saved protocol summary to {run_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
