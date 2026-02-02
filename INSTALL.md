# Install & run – openclaw-mcp

**MCP server (stdio)** and **webapp (React dashboard)**. Both use OpenClaw Gateway and Moltbook; install OpenClaw separately.

**Clone-based** – no PyPI package yet. Clone, run scripts, done.

## Quick start

**1. Clone**
```powershell
git clone https://github.com/sandraschi/openclaw-mcp.git
cd openclaw-mcp
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
Add openclaw-mcp to your MCP client config (stdio, cwd = cloned repo). See **MCP config snippet** and **MCP client config locations** below.

## MCP config snippet

Add this to your MCP client config file (inside the `mcpServers` object for Cursor/Claude Desktop, or equivalent). Replace `<REPO_ROOT>` with the absolute path to your cloned openclaw-mcp repo (e.g. `D:/Dev/repos/openclaw-mcp`). Use forward slashes in the path.

Copy-paste: see **[snippets/mcp-config-openclaw-mcp.json](snippets/mcp-config-openclaw-mcp.json)** and [snippets/README.md](snippets/README.md). Pattern doc: [mcp-central-docs MCP client config snippets](https://github.com/sandraschi/mcp-central-docs/blob/main/docs/patterns/MCP_CLIENT_CONFIG_SNIPPETS.md).

```json
"openclaw-mcp": {
  "command": "python",
  "args": ["-m", "openclaw_mcp"],
  "env": {
    "PYTHONPATH": "<REPO_ROOT>/src",
    "PYTHONUNBUFFERED": "1"
  }
}
```

Example (Windows):

```json
"openclaw-mcp": {
  "command": "python",
  "args": ["-m", "openclaw_mcp"],
  "env": {
    "PYTHONPATH": "D:/Dev/repos/openclaw-mcp/src",
    "PYTHONUNBUFFERED": "1"
  }
}
```

No `cwd` or editable install needed: `PYTHONPATH` points Python at the repo `src` folder so `openclaw_mcp` is found. Use your system Python or any venv that has the dependencies (run `.\scripts\install.ps1` once to install deps into the repo venv, then set `"command": "<REPO_ROOT>/.venv/Scripts/python.exe"` if you prefer that venv).

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
| `OPENCLAW_LOG_DIR` | `~/.openclaw-mcp/logs` |
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
2. **Disconnect openclaw-mcp** – So this app stops talking to OpenClaw:
   - **MCP**: Remove or comment out the openclaw-mcp server from your Cursor/Claude Desktop MCP config. Unset `OPENCLAW_GATEWAY_URL` and `OPENCLAW_GATEWAY_TOKEN` in the environment that starts the MCP server (e.g. in your shell profile or the config that launches the server).
   - **Webapp**: Unset `OPENCLAW_GATEWAY_URL` and `OPENCLAW_GATEWAY_TOKEN` in the environment where you run the webapp (e.g. before running `start.ps1`), then restart.
3. **Uninstall the OpenClaw CLI** (optional, full removal):
   - **npm**: `npm uninstall -g openclaw`
   - **install script**: If you used `curl -fsSL https://openclaw.ai/install.sh | bash`, check [docs.openclaw.ai](https://docs.openclaw.ai) for uninstall or remove the binary and any symlinks it created.
4. **Remove config and data** (optional): Delete `~/.openclaw` (or the path documented by OpenClaw) to remove Gateway config, skills cache, and local data.

After this, openclaw-mcp will no longer reach OpenClaw; Gateway-dependent features (Ask OpenClaw, Channels, Routes, Integrations) will fail until you reconfigure or reinstall. The webapp **Security** page and the MCP tool **clawd_openclaw_disconnect** summarize this and link here.

## OpenClaw Platform Installation

> [!WARNING]
> **Security Advisory (Feb 2, 2026)**: OpenClaw has a critical 1-click RCE vulnerability (CVE-2026-25253) and 341+ malicious skills on ClawHub marketplace. We **strongly recommend** Installation Method 2 (VirtualBox) for maximum isolation.

openclaw-mcp requires the OpenClaw platform to be installed separately. Choose an installation method based on your security requirements:

- **Method 1 (Docker)**: Fast setup, moderate security
- **Method 2 (VirtualBox + Docker)**: ✅ **RECOMMENDED** - Maximum security, complete isolation
- **Method 3 (Naked install)**: ⚠️ **NOT RECOMMENDED** - No sandboxing

---

### Installation Method 1: Docker (Direct on Host)

Insights from [Simon Willison's TIL](https://til.simonwillison.net/llms/openclaw-docker) on running the OpenClaw platform in Docker:

#### 1. Run via Docker Compose
Clone the [OpenClaw platform repo](https://github.com/openclaw/openclaw) and use their `docker-compose.yml`.

#### 2. Setup Prompts
- **Onboarding**: Choose `manual` and `Local gateway`.
- **Model**: OpenAI Codex with ChatGPT OAuth is a good cost-capped choice.
- **Tailscale**: Skip if it causes connectivity issues during initial setup.

#### 3. Pairing and Admin
If you use Telegram, create a bot via [@BotFather](https://t.me/BotFather) and pair it:
```bash
docker compose run --rm openclaw-cli pairing approve telegram <CODE>
```

To list and approve devices (to fix `pairing required` errors):
```bash
docker compose exec openclaw-gateway node dist/index.js devices list
docker compose exec openclaw-gateway node dist/index.js devices approve <REQUEST_ID>
```

#### 4. Customization
To install extra packages (like `ripgrep`) inside the container:
```bash
docker compose exec -u root openclaw-gateway apt-get update && apt-get install -y ripgrep
```

#### 5. Get Access Token
```bash
docker compose run --rm openclaw-cli dashboard --no-open
```

Access OpenClaw: `http://localhost:18789?token=YOUR_TOKEN`

---

### Installation Method 2: VirtualBox + Docker ✅ RECOMMENDED

**Complete Step-by-Step Guide**: See [docs/INSTALL_VIRTUALBOX.md](docs/INSTALL_VIRTUALBOX.md)

For maximum security, run OpenClaw inside a **VirtualBox VM** with Docker. This ensures the agent and its tools (browser, bash) cannot "jump out" to your physical host.

#### Quick Overview

**Requirements:**
- VirtualBox 7.2.6+
- 8GB RAM minimum (16GB recommended)
- 40GB free disk space
- ~50 minutes total setup time

**What You Get:**
- **Double isolation**: Container → VM → Host
- **Network security**: Host-Only adapter for local access, Tailscale for remote
- **Easy recovery**: VM snapshots for instant rollback
- **Peace of mind**: Agent cannot access your host filesystem

#### High-Level Steps

1. **Download Ubuntu Server 24.04 ISO** (~2.6 GB)
2. **Create VirtualBox VM**
   - 4-8GB RAM, 40GB disk
   - NAT + Host-Only network adapters
3. **Install Ubuntu Server** (~10 minutes)
4. **Install Docker** in the VM
5. **Install OpenClaw** via Docker Compose inside VM
6. **Install Tailscale** (optional, for remote access)
7. **Configure openclaw-mcp** on host to point to VM IP

#### Network Access

You'll access OpenClaw via:
- **Host-Only Network** (local): `http://192.168.56.101:18789`
- **Tailscale** (remote): `http://100.64.X.X:18789`

#### VM Configuration Snapshot

```bash
# Inside VM: Get Host-Only IP
ip addr show enp0s8

# Inside VM: Get Tailscale IP
tailscale ip -4

# Inside VM: Get access token
docker compose run --rm openclaw-cli dashboard --no-open
```

#### Security Hardening

**Firewall (inside VM):**
```bash
sudo apt install -y ufw
sudo ufw allow 22/tcp
sudo ufw allow from 192.168.56.0/24 to any port 18789
sudo ufw allow from 100.64.0.0/10 to any port 18789
sudo ufw enable
```

**On your Windows host**, configure openclaw-mcp:
```json
"openclaw-mcp": {
  "command": "python",
  "args": ["-m", "openclaw_mcp"],
  "env": {
    "PYTHONPATH": "D:/Dev/repos/openclaw-mcp/src",
    "PYTHONUNBUFFERED": "1",
    "OPENCLAW_GATEWAY_URL": "http://192.168.56.101:18789",
    "OPENCLAW_GATEWAY_TOKEN": "YOUR_TOKEN_HERE"
  }
}
```

**Full detailed guide with troubleshooting**: [docs/INSTALL_VIRTUALBOX.md](docs/INSTALL_VIRTUALBOX.md)

---

### Installation Method 3: Naked Install ⚠️ NOT RECOMMENDED

Installing OpenClaw directly on your host OS (via `npm install -g openclaw` or install script) provides **no sandboxing** and exposes your system to:

- ❌ Full filesystem access
- ❌ Shell command execution with your user permissions
- ❌ CVE-2026-25253 RCE vulnerability
- ❌ Malicious skills from ClawHub marketplace

If you must use naked install:

1. **Install**:
   ```bash
   npm install -g openclaw@latest
   # OR
   curl -fsSL https://openclaw.ai/install.sh | bash
   ```

2. **Configure** OpenClaw via `~/.openclaw/openclaw.json`

3. **Bind to localhost only**:
   ```json
   {
     "gateway": {
       "bind": "127.0.0.1",
       "port": 18789
     }
   }
   ```

4. **Enable all security features** in config

5. **Never install skills from ClawHub** until malware campaign is resolved

**We strongly discourage this method.** Use Method 2 (VirtualBox) instead.

---
