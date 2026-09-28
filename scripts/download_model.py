"""Download a model snapshot only when the user explicitly asks for it."""
from __future__ import annotations

import argparse
from pathlib import Path
from huggingface_hub import snapshot_download

parser = argparse.ArgumentParser()
parser.add_argument("repo_id")
parser.add_argument("--output", default="models/checkpoints")
args = parser.parse_args()

target = Path(args.output) / args.repo_id.replace("/", "__")
snapshot_download(repo_id=args.repo_id, local_dir=target)
print(f"Downloaded {args.repo_id} to {target}")
