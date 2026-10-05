"""Audit provenance and calibration readiness of the digital twin parameters."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "calibration" / "model_parameters.yaml"
ALLOWED_STATUS = {"official", "cad-derived", "measured", "provisional"}
ALLOWED_CONFIDENCE = {"none", "low", "medium", "high"}


def audit(path: Path, require_measured: bool = False) -> tuple[list[str], dict[str, int]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    counts = {status: 0 for status in ALLOWED_STATUS}
    parameters = payload.get("parameters", {})
    if not parameters:
        errors.append("manifest has no parameters")
    for name, item in parameters.items():
        status = item.get("status")
        confidence = item.get("confidence")
        if status not in ALLOWED_STATUS:
            errors.append(f"{name}: invalid status {status!r}")
        else:
            counts[status] += 1
        if confidence not in ALLOWED_CONFIDENCE:
            errors.append(f"{name}: invalid confidence {confidence!r}")
        for field in ("unit", "source", "verify"):
            if not item.get(field):
                errors.append(f"{name}: missing {field}")
        if status == "measured" and item.get("value") is None:
            errors.append(f"{name}: measured parameter has no value")
        if require_measured and status == "provisional":
            errors.append(f"{name}: still provisional")
    return errors, counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--require-measured", action="store_true")
    args = parser.parse_args()
    errors, counts = audit(args.manifest, args.require_measured)
    print("Parameter provenance:", ", ".join(f"{k}={counts[k]}" for k in sorted(counts)))
    if errors:
        raise SystemExit("PARAMETER AUDIT FAILED\n- " + "\n- ".join(errors))
    print("PASS: every model parameter has provenance, units and a verification method")


if __name__ == "__main__":
    main()

