#!/usr/bin/env bash
set -euo pipefail

isaac_root="${1:?Usage: isaac/open.sh /path/to/isaac-sim}"
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
usd="$repo_dir/isaac/generated/xlerobot/xlerobot.usda"
[[ -f "$usd" ]] || { echo "Run isaac/import.sh first" >&2; exit 1; }
exec "$isaac_root/python.sh" "$repo_dir/isaac/open_usd.py" "$usd"
