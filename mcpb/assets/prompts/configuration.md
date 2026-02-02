# openclaw-mcp Configuration

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENCLAW_GATEWAY_URL` | Gateway HTTP base URL | `http://127.0.0.1:18789` |
| `OPENCLAW_GATEWAY_TOKEN` | Bearer token for Tools Invoke / Webhooks | (none) |
| `OPENCLAW_OPENCLAW_PATH` | Path to openclaw CLI binary | `openclaw` |
| `MOLTBOOK_API_KEY` | Moltbook agent API key (for moltbook tools) | (none) |

## Gateway Auth

OpenClaw Gateway supports:
- `gateway.auth.mode: "token"` — Use `gateway.auth.token` or `OPENCLAW_GATEWAY_TOKEN`
- `gateway.auth.mode: "password"` — Use `gateway.auth.password` or `OPENCLAW_GATEWAY_PASSWORD`

For Tools Invoke and Webhooks, send:
```
Authorization: Bearer <token>
```

## Webhooks

Webhooks require `hooks.enabled: true` and `hooks.token` in Gateway config. Use the same token as Gateway auth or a dedicated hook token.

## Workspace Path

Default: `~/.openclaw/workspace`. Override via `OPENCLAW_WORKSPACE_PATH` if needed.

## Moltbook

For Moltbook operations (future tools):
- Register agent at https://www.moltbook.com/api/v1/agents/register
- Save API key to `MOLTBOOK_API_KEY`
- Always use `https://www.moltbook.com` (with www) — redirect without www strips Authorization header
