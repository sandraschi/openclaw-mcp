# clawd-mcp start script - webapp API (5181) and webapp dev server (5180)
# Run from repo root or scripts/. Kills existing processes on 5181/5180, then opens two windows.

$ErrorActionPreference = "Stop"
$projectRoot = if ($PSScriptRoot) { (Resolve-Path (Join-Path (Split-Path -Parent $PSScriptRoot) ".")).Path } else { (Get-Location).Path }
if (-not (Test-Path (Join-Path $projectRoot "webapp_api\main.py"))) {
    $projectRoot = (Get-Location).Path
}
Set-Location $projectRoot

# Kill zombies on 5181 and 5180 and close their parent PowerShell windows.
# Kills port-owning process then its parent (the window that started it).
function Stop-ProcessOnPort {
    param([int]$Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $conn) { return }
    $currentPid = $PID
    $toKill = $conn.OwningProcess | Sort-Object -Unique
    $parentPids = @()
    foreach ($childPid in $toKill) {
        $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $childPid" -ErrorAction SilentlyContinue
        if ($proc -and $proc.ParentProcessId -and $proc.ParentProcessId -ne 0 -and $proc.ParentProcessId -ne $currentPid) {
            $parentPids += $proc.ParentProcessId
        }
        Stop-Process -Id $childPid -Force -ErrorAction SilentlyContinue
        Write-Host "Killed PID $childPid on port $Port"
    }
    $parentPids | Sort-Object -Unique | ForEach-Object {
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
        Write-Host "Closed parent window (PID $_)"
    }
}
Stop-ProcessOnPort -Port 5181
Stop-ProcessOnPort -Port 5180

# Kill watchfiles (uvicorn --reload) only for this project; leave other webapps' watchers alone.
$currentPid = $PID
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -match 'watchfiles' -and $_.CommandLine -and $_.CommandLine.IndexOf($projectRoot, [StringComparison]::OrdinalIgnoreCase) -ge 0
} | ForEach-Object {
    $childPid = $_.ProcessId
    $parentPid = $_.ParentProcessId
    Stop-Process -Id $childPid -Force -ErrorAction SilentlyContinue
    Write-Host "Killed watchfiles PID $childPid"
    if ($parentPid -and $parentPid -ne 0 -and $parentPid -ne $currentPid) {
        Stop-Process -Id $parentPid -Force -ErrorAction SilentlyContinue
        Write-Host "Closed parent window (PID $parentPid)"
    }
}

Start-Sleep -Seconds 2

$srcPath = (Join-Path $projectRoot "src") -replace "'", "''"
$webappPath = (Join-Path $projectRoot "webapp") -replace "'", "''"

Write-Host "Starting webapp API (port 5181)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='$srcPath'; try { uvicorn webapp_api.main:app --reload --port 5181 } finally { Read-Host 'Press Enter to close' }"

Start-Sleep -Seconds 2
Write-Host "Starting webapp dev server (port 5180)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$webappPath'; try { npm run dev } finally { Read-Host 'Press Enter to close' }"

Write-Host "API: http://127.0.0.1:5181  Webapp: http://localhost:5180"
