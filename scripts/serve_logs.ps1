# openclaw-mcp log server - serves MCP log file for webapp Logger modal
# Run from repo root or scripts/. Default: http://127.0.0.1:8765

$ErrorActionPreference = "Stop"
$projectRoot = if ($PSScriptRoot) { (Resolve-Path (Join-Path (Split-Path -Parent $PSScriptRoot) ".")).Path } else { (Get-Location).Path }
if (-not (Test-Path (Join-Path $projectRoot "src\openclaw_mcp"))) {
    $projectRoot = (Get-Location).Path
}
Set-Location $projectRoot
$env:PYTHONPATH = (Join-Path $projectRoot "src")
python -m openclaw_mcp.serve_logs
