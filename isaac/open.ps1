param(
    [string]$IsaacRoot = "C:\isaacsim",
    [string]$Usd = ""
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path (Resolve-Path -LiteralPath $IsaacRoot).Path "python.bat"
if ($Usd) {
    $usdPath = (Resolve-Path -LiteralPath (Join-Path $repo $Usd)).Path
} else {
    $latest = Get-ChildItem -LiteralPath (Join-Path $repo "isaac/generated") -Recurse -File -Filter "xlerobot_v04.usda" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $latest) { throw "Run isaac/import.ps1 first." }
    $usdPath = $latest.FullName
}
Write-Host "Opening Isaac USD: $usdPath"
& $python (Join-Path $repo "isaac/open_usd.py") $usdPath
