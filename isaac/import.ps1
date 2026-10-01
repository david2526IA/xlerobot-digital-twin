param(
    [Parameter(Mandatory = $true)]
    [string]$IsaacRoot,
    [string]$Output = "isaac/generated"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path -LiteralPath $IsaacRoot).Path
$python = Join-Path $root "python.bat"
$importer = Join-Path $root "standalone_examples/api/isaacsim.asset.importer.urdf/urdf_import.py"
if (-not (Test-Path -LiteralPath $python)) { throw "Isaac Sim python.bat not found at $python" }
if (-not (Test-Path -LiteralPath $importer)) { throw "Isaac Sim URDF importer not found at $importer" }

$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$urdf = Join-Path $repo "robot_description/xlerobot_v04.urdf"
$outputPath = Join-Path $repo $Output
New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

& $python $importer --urdf $urdf --usd-path $outputPath --no-fix-base --no-merge-fixed-joints --joint-drive-type force --joint-target-type position
if ($LASTEXITCODE -ne 0) { throw "Isaac URDF import failed." }
$expectedUsd = Join-Path $outputPath "xlerobot_v04/xlerobot_v04.usda"
if (Test-Path -LiteralPath $expectedUsd) {
    $generated = Get-Item -LiteralPath $expectedUsd
} else {
    $generated = Get-ChildItem -LiteralPath $outputPath -Recurse -File |
        Where-Object { $_.Extension -in @(".usd", ".usda", ".usdc") } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}
if (-not $generated) { throw "Importer did not create a USD below $outputPath" }

& $python (Join-Path $repo "isaac/postprocess_v04.py") $generated.FullName
if ($LASTEXITCODE -ne 0) { throw "Isaac camera post-processing failed." }
& $python (Join-Path $repo "isaac/verify_usd.py") $generated.FullName
if ($LASTEXITCODE -ne 0) { throw "Imported USD verification failed." }
Write-Host "Isaac USD ready: $($generated.FullName)"
