$ErrorActionPreference = "Stop"
$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Missing .venv. Run scripts\bootstrap.ps1 first."
}
& $python scripts\validate_twin.py
& $python scripts\validate_isaac_source.py
& $python -m pytest -q
& $python scripts\record_rollouts.py --episodes 1 --output outputs\verification_rollout
Write-Host "Verification complete."
