param(
    [string]$IsaacRoot = "C:\isaacsim",
    [string]$Usd = "isaac/generated/xlerobot/xlerobot.usda"
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path (Resolve-Path -LiteralPath $IsaacRoot).Path "python.bat"
$usdPath = (Resolve-Path -LiteralPath (Join-Path $repo $Usd)).Path
& $python (Join-Path $repo "isaac/open_usd.py") $usdPath
