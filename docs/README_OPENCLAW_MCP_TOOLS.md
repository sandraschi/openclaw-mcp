# openclaw-mcp Server and Tools

**FastMCP 2.14+** MCP server exposing OpenClaw and Moltbook operations to Cursor, Claude Desktop, and other MCP clients.

**Webapp parity**: The webapp dashboard mirrors many tools via the webapp API (Channels page -> POST /api/channels; Routes page -> POST /api/routing; Integrations -> /api/gateway/status, /api/skills). See [README_WEBAPP.md](README_WEBAPP.md).

## MCP client config

Add openclaw-mcp to your MCP client config (Cursor, Claude Desktop, Windsurf, Zed, etc.). Use the snippet in [INSTALL.md](../INSTALL.md#mcp-config-snippet) with `env.PYTHONPATH` set to `<REPO_ROOT>/src` and `PYTHONUNBUFFERED=1`; no `cwd` or editable install required. Client config file locations: [INSTALL.md#mcp-client-config-locations](../INSTALL.md#mcp-client-config-locations).

## Architecture

```
MCP Clients (Cursor, Claude Desktop)
    |
    v
openclaw-mcp (stdio)
    |
    +-- clawd_agent     -> OpenClaw Gateway (Tools Invoke, Webhooks)
    +-- clawd_sessions  -> OpenClaw Gateway (sessions_*)
    +-- clawd_channels  -> OpenClaw Gateway (channels: list, config, send, recent)
    +-- clawd_routing   -> OpenClaw Gateway (routing rules, update, test, session lookup)
    +-- clawd_skills    -> Local workspace + ClawHub
    +-- clawd_gateway   -> Gateway health + openclaw doctor
    +-- clawd_openclaw_disconnect -> Disconnect/remove OpenClaw (steps + doc link; no side effects)
    +-- clawd_security  -> Audit, skill scan, hardening, provision_sandbox
    +-- clawd_moltbook  -> Feed, search, post, comment, upvote, heartbeat
    |
    v
OpenClaw Gateway (HTTP :18789)
```

## Tool Design

### Portmanteau Pattern

Tools are consolidated into logical groups. Each tool has an `operation` parameter to select the action. Reduces tool explosion while keeping full functionality.

### Dialogic Returns

All tools return:

```json
{
  "success": true,
  "message": "Natural language summary for the user",
  "data": { ... }
}
```

Use `message` for conversational replies; use `data` for structured processing.

### Context Usage

Tools accept `ctx: Context` for `ctx.info()` logging and `ctx.report_progress()`.

---

## Tools Reference

### clawd_agent

Agent invocation and messaging.

| Operation | Description | Backend |
|-----------|-------------|---------|
| `wake` | Trigger heartbeat / wake main session | `POST /hooks/wake` |
| `run_agent` | Run isolated agent turn; return to MCP | `POST /hooks/agent` (deliver: false) — *pending* |
| `send_message` | Send message to agent; optionally deliver to channel | `POST /hooks/agent` — *pending* |

**Parameters**: `operation`, `message`, `session_key`, `channel`, `to`, `deliver`, `thinking`, `timeout_seconds`

---

### clawd_channels

OpenClaw channel visibility and messaging (WhatsApp, Telegram, Discord, Slack, etc.).

| Operation | Description | Backend |
|-----------|-------------|---------|
| `list_channels` | Enumerate active channels and connection status | `POST /tools/invoke` tool: `channels` action: `list_channels` |
| `get_channel_config` | Read channel settings (allowFrom, routing rules) | `POST /tools/invoke` tool: `channels` action: `get_channel_config` |
| `send_message` | Route message to channel | `POST /tools/invoke` tool: `channels` action: `send_message` |
| `get_recent_messages` | Pull last N messages from a channel | `POST /tools/invoke` tool: `channels` action: `get_recent_messages` |

**Parameters**: `operation`, `channel`, `to`, `message`, `limit` (default 20), `session_key`, `args`

**Note**: Requires Gateway to expose the `channels` tool. If not yet available, the call returns a clear error.

---

### clawd_routing

Message routing topology (channels to agents).

| Operation | Description | Backend |
|-----------|-------------|---------|
| `get_routing_rules` | List channel-to-agent mapping | `POST /tools/invoke` tool: `routing` action: `get_routing_rules`; fallback: read `~/.openclaw/openclaw.json` |
| `update_routing` | Change channel-to-agent mappings (write; use with care) | `POST /tools/invoke` tool: `routing` action: `update_routing` |
| `test_routing` | Simulate inbound message routing (dry-run) | `POST /tools/invoke` tool: `routing` action: `test_routing` |
| `get_session_by_channel` | Find session from channel + peer | `POST /tools/invoke` tool: `routing` action: `get_session_by_channel` |

**Parameters**: `operation`, `channel`, `agent`, `peer`, `body`, `session_key`, `args`

**Fallback**: If the Gateway does not expose the routing tool, `get_routing_rules` may return data from OpenClaw config when present.

---

### clawd_sessions

Session discovery and agent-to-agent coordination.

| Operation | Description | Backend |
|-----------|-------------|---------|
| `list` | List active sessions (agents) and metadata | `POST /tools/invoke` tool: `sessions_list` |
| `history` | Fetch transcript for a session | `POST /tools/invoke` tool: `sessions_history` |
| `send` | Message another session (agent-to-agent) | `POST /tools/invoke` tool: `sessions_send` |

**Parameters**: `operation`, `session_key`, `args`

---

### clawd_skills

Skills management.

| Operation | Description | Backend |
|-----------|-------------|---------|
| `list` | List installed skills in workspace | Read `workspace/skills/` |
| `read` | Read SKILL.md content for a skill | File read |

**Parameters**: `operation`, `skill_name`, `workspace_path`

**Future**: `search` (ClawHub), `install`, `sync` (Advanced Memory)

---

### clawd_gateway

Gateway status and health.

| Operation | Description | Backend |
|-----------|-------------|---------|
| `status` | Gateway reachable? Tools Invoke probe | `POST /tools/invoke` sessions_list |
| `health` | Health check | Same |
| `doctor` | Run `openclaw doctor` | Subprocess |

**Parameters**: `operation`

---

### clawd_openclaw_disconnect

Disconnect from OpenClaw and get removal steps (informational only; no side effects).

| Description | Backend |
|-------------|---------|
| Returns steps to disconnect (unset env, remove from MCP config), optional uninstall of OpenClaw CLI, optional removal of `~/.openclaw`. Link to [INSTALL.md#removing-openclaw](../INSTALL.md#removing-openclaw). | Static |

**Parameters**: none

Use when the user wants to stop using OpenClaw (e.g. after security advisories or deciding it is not for them). Webapp Security page has the same steps and link.

---

### clawd_security

OpenClaw security audit and hardening (Auth0, Intruder).

| Operation | Description | Backend |
|-----------|-------------|---------|
| `audit` | Gateway bind, auth, token, doctor | HTTP + subprocess |
| `check_skills` | Scan workspace skills for suspicious patterns | File scan |
| `validate_config` | Validate gateway.bind, allowFrom, tools.allow | JSON config |
| `recommendations` | Return hardening checklist | Static |
| `provision_sandbox` | Orchestration playbook for VM sandbox (virtualization-mcp) | Static |

**Parameters**: `operation`, `workspace_path` (optional)

**Optional mount**: `CLAWD_MOUNT_VBOX=1` mounts virtualization-mcp at `vbox_*` for VM provisioning.

See [SECURITY_HARDENING.md](SECURITY_HARDENING.md).

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENCLAW_GATEWAY_URL` | Gateway HTTP base | `http://127.0.0.1:18789` |
| `OPENCLAW_GATEWAY_TOKEN` | Bearer token for Tools Invoke / Webhooks | (none) |
| `OPENCLAW_OPENCLAW_PATH` | Path to openclaw CLI | `openclaw` |
| `MOLTBOOK_API_KEY` | Moltbook agent API key | (none) |
| `OPENCLAW_MOLTBOOK_URL` | Moltbook API base | `https://www.moltbook.com/api/v1` |

---

## Run

```bash
python -m openclaw_mcp
```

Add to Cursor/Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "openclaw-mcp": {
      "command": "python",
      "args": ["-m", "openclaw_mcp"],
      "env": {
        "PYTHONPATH": "D:/Dev/repos/openclaw-mcp/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

## MCPB Packaging

Extensive prompt templates in `mcpb/assets/prompts/`:

- `system.md`, `user.md`, `quick-start.md`, `configuration.md`, `troubleshooting.md`, `examples.json`

Build: `mcpb build`
