$ErrorActionPreference = "Stop"
$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Missing .venv. Run scripts\bootstrap.ps1 first."
}
function Invoke-Checked {
    param([string[]]$Arguments)
    & $python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed: python $Arguments" }
}
Invoke-Checked @("scripts\validate_twin.py")
Invoke-Checked @("scripts\validate_isaac_source.py")
Invoke-Checked @("scripts\verify_official_assets.py")
Invoke-Checked @("scripts\validate_v04_meshes.py")
Invoke-Checked @("scripts\generate_v04_urdf.py")
Invoke-Checked @("scripts\validate_v04_description.py")
Invoke-Checked @("scripts\audit_model_parameters.py")
Invoke-Checked @("-m", "pytest", "-q")
Invoke-Checked @("scripts\record_rollouts.py", "--episodes", "1", "--output", "outputs\verification_rollout")
Write-Host "Verification complete."
