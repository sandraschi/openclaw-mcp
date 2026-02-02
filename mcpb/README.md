# openclaw-mcp MCPB Package

**FastMCP 2.14+** server for OpenClaw and Moltbook ecosystem integration.

## Current MCPB packing standard

- **Manifest v0.2** – `manifest.json` in this directory.
- **Full source in package** – Package must include server source. Build copies repo `src/` into `mcpb/src/` before packing.
- **No dependencies in package** – Runtime (e.g. Claude Desktop) installs dependencies; package is dependency-free.
- **Output** – Built `.mcpb` goes in repo root `dist/`.

## Directory layout (before pack)

```
mcpb/
  manifest.json       # v0.2 manifest, entry_point src/openclaw_mcp/server.py
  assets/
    prompts/          # system.md, user.md, quick-start.md, configuration.md, troubleshooting.md, examples.json
    icon.png          # optional 256x256 PNG
  src/                # COPIED at build time from repo src/
    openclaw_mcp/     # server package
```

## Build (two steps)

**Step 1 – Copy source into mcpb**

Source must be present under `mcpb/src/` so the package contains full source. Copy from repo root:

```powershell
# From repo root
$mcpbSrc = "mcpb\src"
if (Test-Path $mcpbSrc) { Remove-Item -Recurse -Force $mcpbSrc }
New-Item -ItemType Directory -Force -Path $mcpbSrc | Out-Null
Copy-Item -Path "src\openclaw_mcp" -Destination "$mcpbSrc\openclaw_mcp" -Recurse -Force
```

**Step 2 – Pack**

```powershell
# From repo root
New-Item -ItemType Directory -Force -Path dist | Out-Null
mcpb pack mcpb "dist/openclaw-mcp-0.1.0.mcpb"
```

Or use the script (does both steps):

```powershell
.\scripts\mcpb-build.ps1
```

Or from just: `just mcpb`.

Output: `dist/openclaw-mcp-0.1.0.mcpb` (includes `src/openclaw_mcp/`, `assets/prompts/`, `manifest.json`).

## Contents

- **assets/prompts/** – system.md, user.md, quick-start.md, configuration.md, troubleshooting.md, examples.json.
- **src/openclaw_mcp/** – Server source (copied at build time).

## References

- [openclaw.ai](https://openclaw.ai)
- [moltbook.com](https://moltbook.com)
- [docs.openclaw.ai](https://docs.openclaw.ai)
- MCP Central Docs: `sota-scripts/mcpb-packaging/README.md` (workspace standard)
