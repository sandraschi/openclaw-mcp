# openclaw-mcp Architecture

One-page overview of repo layout, MCP vs webapp API, and data flow.

**Last updated**: 2025-02-01

## Repo layout

```
openclaw-mcp/
├── src/openclaw_mcp/        # MCP server (FastMCP 2.14+, stdio)
│   ├── config.py
│   ├── gateway_client.py
│   ├── logging_config.py
│   ├── mcp_instance.py
│   ├── server.py
│   ├── __main__.py
│   └── tools/
│       ├── agent.py        # clawd_agent
│       ├── channels.py     # clawd_channels
│       ├── gateway.py      # clawd_gateway
│       ├── moltbook.py     # clawd_moltbook
│       ├── routing.py      # clawd_routing
│       ├── security.py     # clawd_security
│       ├── sessions.py     # clawd_sessions
│       └── skills.py       # clawd_skills
├── webapp/                  # React + Vite + Tailwind (port 5180)
│   └── src/
│       ├── App.tsx
│       ├── components/     # Layout, Sidebar, Topbar, modals
│       ├── context/        # LogContext
│       ├── pages/          # Startpage, AI, Channels, Routes, Diagram, Statistics, Moltbook, etc.
│       ├── services/       # api.ts
│       └── utils/
├── webapp_api/              # FastAPI (port 5181)
│   ├── main.py             # /api/ask, /api/gateway/status, /api/skills, /api/clawnews,
│   │                       # /api/ollama/*, /api/channels, /api/routing
│   ├── ollama_client.py
│   └── ollama_preprompt.txt
├── scripts/
│   ├── start.ps1           # Kill 5181/5180, start API + webapp (PowerShell)
│   ├── start.bat           # Same (CMD)
│   ├── check.ps1           # Ruff, mypy, pytest
│   └── serve_logs.py       # (in src/openclaw_mcp) Log server for Logger modal
├── mcpb/                    # MCPB packaging
├── tests/
├── docs/
└── SECURITY.md, README.md
```

## MCP vs webapp API

| Aspect | MCP server | Webapp API |
|--------|------------|------------|
| **Transport** | stdio (Cursor, Claude Desktop) | HTTP :5181 (browser via Vite proxy) |
| **Entry** | `python -m openclaw_mcp` | `uvicorn webapp_api.main:app --port 5181` |
| **Tools** | clawd_agent, clawd_sessions, clawd_channels, clawd_routing, clawd_skills, clawd_gateway, clawd_security, clawd_moltbook | Same operations via POST /api/channels, POST /api/routing, POST /api/ask, etc. |
| **Auth** | None (local) | CORS to 5180; Gateway token via backend env |
| **Purpose** | AI assistants (MCP clients) | Human dashboard (React) |

The webapp does not duplicate MCP logic: it calls the same Gateway (and optionally Ollama) via the webapp API. Channels and routing pages call POST /api/channels and POST /api/routing, which proxy to Gateway tools_invoke (same as clawd_channels / clawd_routing).

## Data flow

1. **MCP path**: Cursor/Claude → stdio → openclaw-mcp → GatewayClient → OpenClaw Gateway (:18789). Optional: clawd_moltbook → Moltbook API; clawd_security + CLAWD_MOUNT_VBOX → virtualization-mcp.

2. **Webapp path**: Browser (:5180) → Vite proxy /api → webapp_api (:5181) → GatewayClient → OpenClaw Gateway. AI page: webapp_api → Ollama (:11434). Diagram/Statistics/Moltbook: no Gateway calls (Diagram: mermaid; Statistics: Gateway + routing fetch; Moltbook: localStorage).

3. **Start scripts**: Kill processes on 5181 and 5180, wait 2s, start API in one window and webapp in another. Windows stay open on exit so errors are visible.

## Configuration

- **Gateway**: OPENCLAW_GATEWAY_URL, OPENCLAW_GATEWAY_TOKEN.
- **Moltbook**: MOLTBOOK_API_KEY, OPENCLAW_MOLTBOOK_URL.
- **Webapp API**: OLLAMA_BASE (Ollama proxy).
- **Logs**: OPENCLAW_LOG_DIR, OPENCLAW_LOG_LEVEL; CLAWD_LOG_SERVER_PORT (log server for Logger modal).
- **Optional**: CLAWD_MOUNT_VBOX=1 (mount virtualization-mcp at vbox_*).

## References

- [README_openclaw_mcp_TOOLS.md](README_openclaw_mcp_TOOLS.md) – tool reference
- [README_WEBAPP.md](README_WEBAPP.md) – webapp pages and API endpoints
- [SECURITY_HARDENING.md](SECURITY_HARDENING.md) – security patterns
