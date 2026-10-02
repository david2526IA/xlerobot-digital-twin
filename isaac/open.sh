#!/usr/bin/env bash
set -euo pipefail

isaac_root="${1:?Usage: isaac/open.sh /path/to/isaac-sim}"
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
usd="${2:-}"
if [[ -z "$usd" ]]; then
  usd="$(find "$repo_dir/isaac/generated" -type f -name 'xlerobot_v04.usda' -printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)"
fi
[[ -f "$usd" ]] || { echo "Run isaac/import.sh first" >&2; exit 1; }
echo "Opening Isaac USD: $usd"
exec "$isaac_root/python.sh" "$repo_dir/isaac/open_usd.py" "$usd"
