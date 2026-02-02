# openclaw-mcp check script - run ruff, mypy, pytest

param(
    [switch]$Ruff,
    [switch]$Mypy,
    [switch]$Test,
    [switch]$All
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    if ($Ruff -or $All) {
        Write-Host "Running ruff check..."
        ruff check src tests
        Write-Host "Running ruff format check..."
        ruff format --check src tests
    }

    if ($Mypy -or $All) {
        Write-Host "Running mypy..."
        mypy src
    }

    if ($Test -or $All) {
        Write-Host "Running pytest..."
        pytest tests -v
    }

    if (-not ($Ruff -or $Mypy -or $Test -or $All)) {
        Write-Host "Usage: .\scripts\check.ps1 -Ruff | -Mypy | -Test | -All"
        Write-Host "  -Ruff  Run ruff check and format"
        Write-Host "  -Mypy  Run mypy type check"
        Write-Host "  -Test  Run pytest"
        Write-Host "  -All   Run all checks"
    }
}
finally {
    Pop-Location
}
