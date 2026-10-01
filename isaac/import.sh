#!/usr/bin/env bash
set -euo pipefail

isaac_root="${1:?Usage: isaac/import.sh /path/to/isaac-sim}"
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="$isaac_root/python.sh"
importer="$isaac_root/standalone_examples/api/isaacsim.asset.importer.mjcf/mjcf_import.py"
output="$repo_dir/isaac/generated"

[[ -x "$python_bin" ]] || { echo "Missing $python_bin" >&2; exit 1; }
[[ -f "$importer" ]] || { echo "Missing $importer" >&2; exit 1; }
mkdir -p "$output"
"$python_bin" "$importer" --mjcf "$repo_dir/assets/xlerobot/xlerobot.xml" --usd-path "$output" --merge-mesh
usd="$output/xlerobot/xlerobot.usda"
[[ -f "$usd" ]] || { echo "Importer did not create $usd" >&2; exit 1; }
"$python_bin" "$repo_dir/isaac/verify_usd.py" "$usd"
echo "Isaac USD ready: $usd"
