#!/usr/bin/env bash
set -euo pipefail

isaac_root="${1:?Usage: isaac/import.sh /path/to/isaac-sim}"
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="$isaac_root/python.sh"
importer="$isaac_root/standalone_examples/api/isaacsim.asset.importer.urdf/urdf_import.py"
output="$repo_dir/isaac/generated"

[[ -x "$python_bin" ]] || { echo "Missing $python_bin" >&2; exit 1; }
[[ -f "$importer" ]] || { echo "Missing $importer" >&2; exit 1; }
mkdir -p "$output"
"$python_bin" "$importer" --urdf "$repo_dir/robot_description/xlerobot_v04.urdf" --usd-path "$output" --no-fix-base --no-merge-fixed-joints --joint-drive-type force --joint-target-type position
usd="$(find "$output" -type f -name 'xlerobot_v04.usda' -printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)"
[[ -n "$usd" && -f "$usd" ]] || { echo "Importer did not create xlerobot_v04.usda below $output" >&2; exit 1; }
"$python_bin" "$repo_dir/isaac/postprocess_v04.py" "$usd"
"$python_bin" "$repo_dir/isaac/verify_usd.py" "$usd"
echo "Isaac USD ready: $usd"
