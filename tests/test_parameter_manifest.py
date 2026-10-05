from pathlib import Path

from scripts.audit_model_parameters import audit


ROOT = Path(__file__).resolve().parents[1]


def test_parameter_manifest_has_complete_provenance():
    errors, counts = audit(ROOT / "calibration" / "model_parameters.yaml")
    assert not errors
    assert sum(counts.values()) >= 16
    assert counts["provisional"] > 0

