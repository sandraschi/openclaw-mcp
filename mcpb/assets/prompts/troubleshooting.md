# openclaw-mcp Troubleshooting

## Gateway Unreachable

**Symptom**: Tools return "Could not reach Gateway" or connection refused.

**Fix**:
1. Ensure OpenClaw Gateway is running: `openclaw gateway --port 18789`
2. Check `OPENCLAW_GATEWAY_URL` — default is `http://127.0.0.1:18789`
3. If Gateway runs remotely, use SSH tunnel or Tailscale Serve

## 401 Unauthorized

**Symptom**: Tools Invoke or Webhooks return 401.

**Fix**:
1. Set `OPENCLAW_GATEWAY_TOKEN` to match `gateway.auth.token` or `OPENCLAW_GATEWAY_TOKEN` in OpenClaw config
2. Check `~/.openclaw/openclaw.json` for `gateway.auth.mode` and `gateway.auth.token`

## 404 Tool Not Available

**Symptom**: Tools Invoke returns 404 for sessions_list or other tool.

**Fix**:
1. Tool may be filtered by policy — check `tools.allow`, `tools.byProvider.allow` in OpenClaw config
2. Ensure Gateway is fully started (Pi agent, etc.)

## openclaw CLI Not Found

**Symptom**: clawd_gateway operation: doctor fails with "openclaw CLI not found".

**Fix**:
1. Install OpenClaw: `npm i -g openclaw` or via install.sh
2. Ensure `openclaw` is on PATH
3. Override via `OPENCLAW_OPENCLAW_PATH` if binary is elsewhere

## Skills Directory Empty

**Symptom**: clawd_skills list returns 0 skills.

**Fix**:
1. Run `openclaw onboard` to set up workspace
2. Install skills from ClawHub: `clawhub install <slug>`
3. Check `~/.openclaw/workspace/skills/` exists

## Moltbook API Errors

**Symptom**: Moltbook tools return auth or redirect errors.

**Fix**:
1. Always use `https://www.moltbook.com` (with www)
2. Never send API key to any domain other than www.moltbook.com
3. Verify claim status: `curl https://www.moltbook.com/api/v1/agents/status -H "Authorization: Bearer YOUR_KEY"`
