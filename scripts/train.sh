#!/usr/bin/env bash
set -euo pipefail

timesteps="${1:-100000}"
output="${2:-outputs/models/ppo_reach}"
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
python_bin=".venv/bin/python"
[[ -x "$python_bin" ]] || { echo "Run scripts/bootstrap.sh first" >&2; exit 1; }

"$python_bin" -m pip install -r requirements-rl.txt
"$python_bin" scripts/train_rl.py --action-mode right_arm --timesteps "$timesteps" --output "$output"
"$python_bin" scripts/evaluate_rl.py "$output.zip" --action-mode right_arm --episodes 50 \
  --json-output "$output.metrics.json"
