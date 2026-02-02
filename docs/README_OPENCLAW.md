# OpenClaw

**Source**: [openclaw.ai](https://openclaw.ai) | [docs.openclaw.ai](https://docs.openclaw.ai) | [GitHub openclaw/openclaw](https://github.com/openclaw/openclaw)

## What Is OpenClaw?

OpenClaw (formerly ClawdBot, Moltbot) is a personal AI assistant platform. "The AI that actually does things." Inbox management, email sending, calendar control, flight check-in—all from WhatsApp, Telegram, or any chat app.

## Core Architecture

```
Gateway (WS + HTTP :18789)
    |
    +-- Channels: WhatsApp, Telegram, Slack, Discord, Signal, iMessage, WebChat, etc.
    +-- Pi Agent: RPC coding agent with tool streaming, block streaming
    +-- Tools: Browser (CDP), bash, cron, webhooks, Gmail Pub/Sub, sessions (agent-to-agent)
    +-- Skills: AgentSkills-compatible SKILL.md folders
```

### Gateway

- **WebSocket** control plane on port 18789 (loopback-first)
- **HTTP APIs**:
  - `POST /tools/invoke` — invoke any Gateway tool directly
  - `POST /hooks/wake` — trigger wake / heartbeat
  - `POST /hooks/agent` — run agent turn, optionally deliver to channel
- **OpenAI Chat Completions** proxy for LLM calls

### Channels

| Channel | Library/Protocol |
|---------|------------------|
| WhatsApp | Baileys |
| Telegram | grammY |
| Slack, Discord | Native APIs |
| Signal, iMessage | BlueBubbles, etc. |
| WebChat | Built-in |

### Pi Agent

RPC-mode coding agent ([badlogic/pi-mono](https://github.com/badlogic/pi-mono)). Supports tool streaming, block streaming. Used by OpenClaw for agentic tasks.

### Tools

- **Browser**: CDP (Chrome DevTools Protocol)
- **Canvas / A2UI**: UI automation
- **bash**: Shell execution
- **cron**: Scheduled jobs
- **webhooks**: Inbound triggers
- **Gmail Pub/Sub**: Email events
- **sessions**: Agent-to-agent (`sessions_list`, `sessions_history`, `sessions_send`)
- **tts**: Text-to-speech (ElevenLabs, OpenAI, or Edge TTS); returns MEDIA path. See [OpenClaw TTS](https://docs.clawd.bot/tts).

### Skills

AgentSkills-compatible modules. Each skill is a folder with `SKILL.md` (YAML frontmatter + Markdown body). **ClawHub** (clawhub.com) is the public registry—565+ skills. Install: `clawhub install <slug>`.

## Install

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
# or
npm i -g openclaw
```

### openclaw-mcp integration

## Configuration

- Config: `~/.openclaw/openclaw.json`
- Workspace: `~/.openclaw/workspace`
- Skills: `~/.openclaw/workspace/skills/`
- Auth: `gateway.auth.mode` (token, password), `gateway.auth.token`, `OPENCLAW_GATEWAY_TOKEN`

## Naming Evolution

- **ClawdBot** — Original name
- **Moltbot** — Rebrand (trademark; "molt" = lobster shedding shell)
- **OpenClaw** — Current primary (openclaw.ai, GitHub)

## Public Reaction

- "Open source built a better version of Siri while Apple slept" — Hesamation
- "First true personal assistant" — MacStories
- "AI as teammate, not tool" — lycfyi
- Karpathy: "Love oracle and Claw"

## Voice (TTS / STT) – piggybacking

openclaw-mcp can use OpenClaw’s TTS (and, where exposed, STT) via the Gateway.

**TTS (text-to-speech)**  
OpenClaw has a Gateway tool `tts` that converts text to speech (ElevenLabs, OpenAI, or Edge TTS). Invoke it with `POST /tools/invoke`: `tool: "tts"`, `args: { text: "..." }`. The result includes a MEDIA path to the generated audio. openclaw-mcp exposes this as the MCP tool `clawd_voice` (operation `tts`, argument `text`). Configure TTS in OpenClaw: `messages.tts` in `~/.openclaw/openclaw.json`; see [OpenClaw TTS](https://docs.clawd.bot/tts).

**STT (speech-to-text)**  
OpenClaw handles voice input in its own pipeline (voice notes, Talk mode, Voice Wake). Transcription hooks and node audio are documented under [Audio and voice notes](https://docs.clawd.bot/nodes/audio) and [Talk mode](https://docs.clawd.bot/nodes/talk). If the Gateway exposes an STT tool via `/tools/invoke`, openclaw-mcp can add a similar proxy later.

## References

- [openclaw.ai](https://openclaw.ai)
- [docs.openclaw.ai](https://docs.openclaw.ai)
- [docs.clawd.bot](https://docs.clawd.bot)
- [clawhub.com](https://clawhub.com)
- [Tools Invoke API](https://docs.clawd.bot/gateway/tools-invoke-http-api)
- [OpenClaw TTS](https://docs.clawd.bot/tts)
- [Audio and voice notes](https://docs.clawd.bot/nodes/audio)
- [Webhooks](https://docs.clawd.bot/automation/webhook)
