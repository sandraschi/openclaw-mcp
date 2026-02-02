# openclaw-mcp User Guide

## Quick Start

1. **Ensure OpenClaw is running**: `openclaw gateway --port 18789`
2. **Configure env**: Set `OPENCLAW_GATEWAY_TOKEN` if your Gateway uses token auth
3. **Add openclaw-mcp to your MCP client** (Cursor, Claude Desktop)
4. **Use tools**: clawd_agent, clawd_sessions, clawd_skills, clawd_gateway

## Tool Usage

### clawd_agent
- `operation: wake` — Trigger heartbeat / wake main session
- `operation: run_agent` — Run isolated agent turn; return response to MCP
- `operation: send_message` — Send message to agent; optionally deliver to channel

### clawd_sessions
- `operation: list` — List active sessions (agents) and metadata
- `operation: history` — Fetch transcript for a session
- `operation: send` — Message another session (agent-to-agent)

### clawd_skills
- `operation: list` — List installed skills in workspace
- `operation: read` — Read SKILL.md content for a skill

### clawd_gateway
- `operation: status` — Gateway status via Tools Invoke
- `operation: health` — Health check
- `operation: doctor` — Run `openclaw doctor` for migrations/config validation

## Dialogic Responses

All tools return:
```json
{
  "success": true,
  "message": "Natural language summary for the user",
  "data": { ... }
}
```

Use `message` for conversational replies; use `data` for structured processing.
