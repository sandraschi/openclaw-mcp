# clawd-mcp install - pip install from source, npm install in webapp
# Run from repo root or scripts/. One-time after clone.

$ErrorActionPreference = "Stop"
$projectRoot = if ($PSScriptRoot) { (Resolve-Path (Join-Path (Split-Path -Parent $PSScriptRoot) ".")).Path } else { (Get-Location).Path }
if (-not (Test-Path (Join-Path $projectRoot "pyproject.toml"))) {
    $projectRoot = (Get-Location).Path
}
Set-Location $projectRoot

Write-Host "Installing Python deps (pip install -e .[dev])..."
pip install -e ".[dev]"
if (-not $?) { exit 1 }

Write-Host "Installing webapp deps (npm install in webapp/)..."
Push-Location (Join-Path $projectRoot "webapp")
npm install
Pop-Location
if (-not $?) { exit 1 }

Write-Host "Done. Run .\scripts\start.ps1 to start API and webapp."
