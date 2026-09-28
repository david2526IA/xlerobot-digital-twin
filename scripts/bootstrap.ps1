$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' not found. Install Python 3.12 first."
}

if (-not (Test-Path -LiteralPath ".venv")) {
    py -3.12 -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
& .\.venv\Scripts\python.exe -m pip install -e .
& .\.venv\Scripts\python.exe scripts\validate_twin.py
& .\.venv\Scripts\python.exe scripts\smoke_env.py

Write-Host "XLeRobot twin ready. Activate with: .\.venv\Scripts\Activate.ps1"
