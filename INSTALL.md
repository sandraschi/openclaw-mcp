# Install & run – clawd-mcp

**MCP server (stdio)** and **webapp (React dashboard)**. Both use OpenClaw Gateway and Moltbook; install OpenClaw separately.

**Clone-based** – no PyPI package yet. Clone, run scripts, done.

## Quick start

**1. Clone**
```powershell
git clone https://github.com/sandraschi/clawd-mcp.git
cd clawd-mcp
```

**2. Install (one-time)**
```powershell
.\scripts\install.ps1
```
Or `scripts\install.bat`. Installs deps from repo; then you can run start.

**3a. Webapp (dashboard + API)**  
From repo root:
```powershell
.\scripts\start.ps1
```
Or `scripts\start.bat`. Kills old processes on 5181/5180 and their windows, kills project-scoped watchfiles; starts API and webapp in two windows. Open http://localhost:5180. API: http://localhost:5181.

**3b. MCP server only**  
Add clawd-mcp to your MCP client config (stdio, cwd = cloned repo). See **MCP config snippet** and **MCP client config locations** below.

## MCP config snippet

Add this to your MCP client config file (inside the `mcpServers` object for Cursor/Claude Desktop, or equivalent). Replace `<REPO_ROOT>` with the absolute path to your cloned clawd-mcp repo (e.g. `D:/Dev/repos/clawd-mcp`). Use forward slashes in the path.

```json
"clawd-mcp": {
  "command": "python",
  "args": ["-m", "clawd_mcp"],
  "env": {
    "PYTHONPATH": "<REPO_ROOT>/src",
    "PYTHONUNBUFFERED": "1"
  }
}
```

Example (Windows):

```json
"clawd-mcp": {
  "command": "python",
  "args": ["-m", "clawd_mcp"],
  "env": {
    "PYTHONPATH": "D:/Dev/repos/clawd-mcp/src",
    "PYTHONUNBUFFERED": "1"
  }
}
```

No `cwd` or editable install needed: `PYTHONPATH` points Python at the repo `src` folder so `clawd_mcp` is found. Use your system Python or any venv that has the dependencies (run `.\scripts\install.ps1` once to install deps into the repo venv, then set `"command": "<REPO_ROOT>/.venv/Scripts/python.exe"` if you prefer that venv).

## MCP client config locations

| Client | Config folder | Config file |
|--------|---------------|-------------|
| **Cursor** | `%APPDATA%\Cursor\User\globalStorage\cursor-storage` | `mcp_config.json` |
| **Claude Desktop** | `%APPDATA%\Claude` | `claude_desktop_config.json` |
| **Windsurf** | `%USERPROFILE%\.codeium\windsurf` | `mcp_config.json` |
| **Zed** | `%APPDATA%\Zed` | `settings.json` |
| **Antigravity** | `%USERPROFILE%\.gemini\antigravity` | `mcp_config.json` |
| **LM Studio** | `%USERPROFILE%\.lmstudio` | `mcp.json` |

`%APPDATA%` is usually `C:\Users\<user>\AppData\Roaming`; `%USERPROFILE%` is `C:\Users\<user>`. Windsurf uses the Codeium path (`.codeium\windsurf`) under `%USERPROFILE%`.

## Configuration

| Variable | Default |
|----------|---------|
| `OPENCLAW_GATEWAY_URL` | `http://127.0.0.1:18789` |
| `OPENCLAW_GATEWAY_TOKEN` | (required when Gateway auth enabled) |
| `MOLTBOOK_API_KEY` | optional |
| `OPENCLAW_LOG_DIR` | `~/.clawd-mcp/logs` |
| `OPENCLAW_LOG_LEVEL` | `INFO` |
| `CLAWD_LOG_SERVER_PORT` | `8765` (webapp Logger modal) |
| `OLLAMA_BASE` | `http://localhost:11434` (webapp Ollama proxy) |
| `LANDING_PAGE_OUTPUT_DIR` | `./generated` (Starter page output) |

## Logging

JSON lines to stderr and rotating file under `OPENCLAW_LOG_DIR`. Webapp **Logger** modal: run `.\scripts\serve_logs.ps1` (default http://127.0.0.1:8765), then Refresh in the modal.

## Checks

```powershell
.\scripts\check.ps1 -All
```
Or `scripts\check.bat` if present. Runs ruff, mypy, pytest.

## Removing OpenClaw

If you want to stop using OpenClaw or remove it (e.g. after reading security advisories or deciding it is not for you):

1. **Stop the Gateway** – Quit any running OpenClaw process (Gateway, Pi agent). Close the terminal or stop the service that runs `openclaw` or the Gateway.
2. **Disconnect clawd-mcp** – So this app stops talking to OpenClaw:
   - **MCP**: Remove or comment out the clawd-mcp server from your Cursor/Claude Desktop MCP config. Unset `OPENCLAW_GATEWAY_URL` and `OPENCLAW_GATEWAY_TOKEN` in the environment that starts the MCP server (e.g. in your shell profile or the config that launches the server).
   - **Webapp**: Unset `OPENCLAW_GATEWAY_URL` and `OPENCLAW_GATEWAY_TOKEN` in the environment where you run the webapp (e.g. before running `start.ps1`), then restart.
3. **Uninstall the OpenClaw CLI** (optional, full removal):
   - **npm**: `npm uninstall -g openclaw`
   - **install script**: If you used `curl -fsSL https://openclaw.ai/install.sh | bash`, check [docs.openclaw.ai](https://docs.openclaw.ai) for uninstall or remove the binary and any symlinks it created.
4. **Remove config and data** (optional): Delete `~/.openclaw` (or the path documented by OpenClaw) to remove Gateway config, skills cache, and local data.

After this, clawd-mcp will no longer reach OpenClaw; Gateway-dependent features (Ask OpenClaw, Channels, Routes, Integrations) will fail until you reconfigure or reinstall. The webapp **Security** page and the MCP tool **clawd_openclaw_disconnect** summarize this and link here.
