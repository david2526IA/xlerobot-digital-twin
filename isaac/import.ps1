param(
    [Parameter(Mandatory = $true)]
    [string]$IsaacRoot,
    [string]$Output = "isaac/generated/xlerobot.usd"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path -LiteralPath $IsaacRoot).Path
$python = Join-Path $root "python.bat"
$importer = Join-Path $root "standalone_examples/api/isaacsim.asset.importer.mjcf/mjcf_import.py"
if (-not (Test-Path -LiteralPath $python)) { throw "Isaac Sim python.bat not found at $python" }
if (-not (Test-Path -LiteralPath $importer)) { throw "Isaac Sim MJCF importer not found at $importer" }

$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$mjcf = Join-Path $repo "assets/xlerobot/xlerobot.xml"
$outputPath = Join-Path $repo $Output
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPath) | Out-Null

& $python $importer --mjcf $mjcf --usd-path $outputPath --merge-mesh
if ($LASTEXITCODE -ne 0) { throw "Isaac MJCF import failed." }
if (-not (Test-Path -LiteralPath $outputPath)) { throw "Importer did not create $outputPath" }

& $python (Join-Path $repo "isaac/verify_usd.py") $outputPath
if ($LASTEXITCODE -ne 0) { throw "Imported USD verification failed." }
Write-Host "Isaac USD ready: $outputPath"
