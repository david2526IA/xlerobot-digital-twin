"""Convert recorded NPZ episodes to the official LeRobotDataset v3 API."""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np

try:
    from lerobot.datasets import LeRobotDataset
except ImportError as exc:
    raise SystemExit("Install LeRobot first: pip install -r requirements-lerobot.txt") from exc

parser = argparse.ArgumentParser()
parser.add_argument("source", help="Directory containing episode_*.npz")
parser.add_argument("--repo-id", default="local/xlerobot_04_sim")
parser.add_argument("--root", default="datasets/lerobot/xlerobot_04_sim")
parser.add_argument("--fps", type=int, default=30)
args = parser.parse_args()
episodes = sorted(Path(args.source).glob("episode_*.npz"))
if not episodes:
    raise SystemExit(f"No episodes found in {args.source}")
sample = np.load(episodes[0])
state_dim, action_dim = sample["observation"].shape[1], sample["action"].shape[1]
features = {
    "observation.state": {"dtype": "float32", "shape": (state_dim,), "names": [f"state_{i}" for i in range(state_dim)]},
    "action": {"dtype": "float32", "shape": (action_dim,), "names": [f"action_{i}" for i in range(action_dim)]},
    "next.reward": {"dtype": "float32", "shape": (1,), "names": ["reward"]},
}
has_images = "neck_rgb" in sample.files
if has_images:
    height, width, channels = sample["neck_rgb"].shape[1:]
    features["observation.images.neck_rgb"] = {"dtype": "video", "shape": (height, width, channels), "names": ["height", "width", "channels"]}
dataset = LeRobotDataset.create(
    repo_id=args.repo_id, root=Path(args.root), fps=args.fps, features=features,
    robot_type="xlerobot_0_4_sim", use_videos=has_images,
)
for episode_path in episodes:
    episode = np.load(episode_path)
    task = str(episode["task"])
    for index in range(len(episode["action"])):
        frame = {
            "observation.state": episode["observation"][index].astype(np.float32),
            "action": episode["action"][index].astype(np.float32),
            "next.reward": np.asarray([episode["reward"][index]], dtype=np.float32),
            "task": task,
        }
        if has_images:
            frame["observation.images.neck_rgb"] = episode["neck_rgb"][index]
        dataset.add_frame(frame)
    dataset.save_episode()
dataset.finalize()
print(f"LeRobotDataset v3 written to {args.root}: episodes={len(episodes)} images={has_images}")
