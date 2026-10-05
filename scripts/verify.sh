#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
python_bin=".venv/bin/python"
[[ -x "$python_bin" ]] || { echo "Run scripts/bootstrap.sh first" >&2; exit 1; }

"$python_bin" scripts/validate_twin.py
"$python_bin" scripts/validate_isaac_source.py
"$python_bin" scripts/verify_official_assets.py
"$python_bin" scripts/validate_v04_meshes.py
"$python_bin" scripts/generate_v04_urdf.py
"$python_bin" scripts/validate_v04_description.py
"$python_bin" scripts/audit_model_parameters.py
"$python_bin" -m pytest -q
"$python_bin" scripts/record_rollouts.py --episodes 1 --output outputs/verification_rollout
echo "Verification complete."
