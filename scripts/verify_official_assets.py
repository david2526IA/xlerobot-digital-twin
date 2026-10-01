"""Verify the pinned official XLeRobot 0.4 CAD snapshot."""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party" / "xlerobot_official"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    manifest_path = SNAPSHOT / "SOURCE.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for record in manifest["files"]:
        path = SNAPSHOT / record["path"]
        if not path.is_file():
            failures.append(f"missing: {record['path']}")
            continue
        actual = sha256(path)
        if actual != record["sha256"]:
            failures.append(
                f"hash mismatch: {record['path']} expected={record['sha256']} actual={actual}"
            )

    license_path = SNAPSHOT / "LICENSE"
    if not license_path.is_file():
        failures.append("missing: LICENSE")

    if failures:
        raise SystemExit("Official asset verification failed:\n" + "\n".join(failures))
    print(
        f"PASS: {len(manifest['files'])} official CAD assets | "
        f"commit={manifest['commit']} | license={manifest['license']}"
    )


if __name__ == "__main__":
    main()
