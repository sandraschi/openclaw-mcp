# Build MCPB package per current standard: copy repo src into mcpb/src, then mcpb pack.
# Run from repo root. Output: dist/openclaw-mcp-<version>.mcpb

$ErrorActionPreference = "Stop"
$repoRoot = $PSScriptRoot + "\.."
$mcpbDir = Join-Path $repoRoot "mcpb"
$srcDir = Join-Path $repoRoot "src"
$mcpbSrc = Join-Path $mcpbDir "src"
$distDir = Join-Path $repoRoot "dist"

# Read version from manifest
$manifestPath = Join-Path $mcpbDir "manifest.json"
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$version = $manifest.version
$name = $manifest.name
$outFile = Join-Path $distDir "$name-$version.mcpb"

if (-not (Test-Path (Join-Path $srcDir "openclaw_mcp"))) {
    Write-Error "Source not found: $srcDir\openclaw_mcp. Run from repo root."
}

# Step 1: Copy source into mcpb/src
if (Test-Path $mcpbSrc) {
    Remove-Item -Recurse -Force $mcpbSrc
}
New-Item -ItemType Directory -Force -Path $mcpbSrc | Out-Null
Copy-Item -Path (Join-Path $srcDir "openclaw_mcp") -Destination (Join-Path $mcpbSrc "openclaw_mcp") -Recurse -Force
Write-Host "Copied src/openclaw_mcp to mcpb/src/openclaw_mcp"

# Step 2: Pack
New-Item -ItemType Directory -Force -Path $distDir | Out-Null
& mcpb pack $mcpbDir $outFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "mcpb pack failed."
}
Write-Host "Built: $outFile"
