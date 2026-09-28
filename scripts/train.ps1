param(
    [int]$Timesteps = 100000,
    [string]$Output = "outputs/models/ppo_reach",
    [string]$Resume = ""
)

$ErrorActionPreference = "Stop"
$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Missing .venv. Run scripts\bootstrap.ps1 first."
}

& $python -m pip install -r requirements-rl.txt
if ($LASTEXITCODE -ne 0) { throw "Could not install RL dependencies." }

$arguments = @(
    "scripts\train_rl.py",
    "--timesteps", $Timesteps,
    "--output", $Output
)
if ($Resume) {
    $arguments += @("--resume", $Resume)
}
& $python @arguments
if ($LASTEXITCODE -ne 0) { throw "PPO training failed." }

& $python scripts\evaluate_rl.py "$Output.zip" --episodes 10
if ($LASTEXITCODE -ne 0) { throw "PPO evaluation failed." }
