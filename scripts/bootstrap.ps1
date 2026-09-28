$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' not found. Install Python 3.12 first."
}

if (-not (Test-Path -LiteralPath ".venv")) {
    py -3.12 -m venv .venv
}

$python = ".\.venv\Scripts\python.exe"
function Invoke-Checked {
    param([string[]]$Arguments)
    & $python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed: python $Arguments" }
}
Invoke-Checked @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Checked @("-m", "pip", "install", "-r", "requirements-dev.txt")
Invoke-Checked @("-m", "pip", "install", "-e", ".")
Invoke-Checked @("scripts\validate_twin.py")
Invoke-Checked @("scripts\smoke_env.py")

Write-Host "XLeRobot twin ready. Activate with: .\.venv\Scripts\Activate.ps1"
