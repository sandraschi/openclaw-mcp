# openclaw-mcp Quick Start

## 1. Install OpenClaw (if not installed)

```bash
npm i -g openclaw
openclaw onboard
```

Or one-liner:
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

## 2. Start OpenClaw Gateway

```bash
openclaw gateway --port 18789 --verbose
```

Or via daemon (after `openclaw onboard --install-daemon`):
```bash
# Gateway runs via launchd/systemd
openclaw status
```

## 3. Configure openclaw-mcp

Create `.env` in openclaw-mcp root:

```
OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789
OPENCLAW_GATEWAY_TOKEN=your-token-if-auth-enabled
```

If Gateway uses loopback-only without auth, token may be omitted.

## 4. Add to Cursor / Claude Desktop

### Cursor (mcp.json)
```json
{
  "mcpServers": {
    "openclaw-mcp": {
      "command": "python",
      "args": ["-m", "openclaw_mcp"],
      "cwd": "D:\\Dev\\repos\\openclaw-mcp"
    }
  }
}
```

### Claude Desktop (claude_desktop_config.json)
```json
{
  "mcpServers": {
    "openclaw-mcp": {
      "command": "python",
      "args": ["-m", "openclaw_mcp"],
      "cwd": "D:\\Dev\\repos\\openclaw-mcp"
    }
  }
}
```

## 5. Test

In Cursor/Claude: "Check OpenClaw gateway status" — use clawd_gateway tool with operation: status.
