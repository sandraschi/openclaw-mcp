# openclaw-mcp Webapp

Dark-themed React + Tailwind dashboard for openclaw-mcp.

## Stack

- **React 18** + TypeScript
- **Vite** 6
- **Tailwind CSS** 3.4
- **React Router** 6
- **Lucide React** (icons)
- **mermaid** (^11) – Diagram page flowcharts
- **class-variance-authority** + **clsx** + **tailwind-merge** (cn utility)

## Theme

- **Background**: `#0a0a0c` (near-black)
- **Accent**: `#f97316` (orange, OpenClaw lobster)
- **Card**: `#0f0f12`, `#16161a`
- **Border**: `#27272a`
- **Font**: Inter (sans), JetBrains Mono (mono)

## Structure

```
webapp/
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── OpenClawInstallBanner.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Topbar.tsx
│   │   └── modals/ (HelpModal, LoggerModal, AuthModal)
│   ├── context/
│   │   └── LogContext.tsx
│   ├── pages/
│   │   ├── Startpage.tsx
│   │   ├── AI.tsx
│   │   ├── Channels.tsx
│   │   ├── Routes.tsx
│   │   ├── Diagram.tsx
│   │   ├── Statistics.tsx
│   │   ├── Moltbook.tsx
│   │   ├── Integrations.tsx
│   │   ├── Clawnews.tsx
│   │   ├── Skills.tsx
│   │   ├── Security.tsx
│   │   ├── StarterPage.tsx   # Generate landing page
│   │   └── Settings.tsx
│   ├── services/
│   │   └── api.ts
│   ├── styles/
│   │   └── main.css
│   └── utils/
│       └── cn.ts
└── public/
    └── favicon.svg
```

**Webapp API** (repo root):

```
webapp_api/
├── main.py          # FastAPI: /api/ask, /api/gateway/status, /api/skills, /api/clawnews,
│                    # /api/ollama/*, /api/channels, /api/routing, /api/openclaw/status, /api/landing-page
├── ollama_client.py
├── landing_page_service.py   # Static landing-site generator (Ecosystem page, DEPLOY.md)
├── landing_assets/           # styles.css, script.js for generated sites
└── ollama_preprompt.txt
```

## Run

**1. Webapp API (optional, for Ask OpenClaw, AI/Ollama, Channels, Routes, Integrations, Clawnews):**

From repo root:

```powershell
pip install -e ".[webapp-api]"
$env:PYTHONPATH = "src"
uvicorn webapp_api.main:app --reload --port 5181
```

**2. Webapp:**

```bash
cd webapp
npm install
npm run dev
```

Port: **5180**. Vite proxies `/api` to http://127.0.0.1:5181.

**One-shot start (two windows):** From repo root run `.\scripts\start.ps1` (PowerShell) or `scripts\start.bat` (CMD). Scripts kill processes on ports 5181 and 5180, close their parent PowerShell windows, and kill watchfiles (uvicorn --reload) only for this project; wait 2s; then start API and webapp in separate windows. Windows stay open on exit (PowerShell: Read-Host; CMD: pause) so errors are visible.

## OpenClaw install banner

On load, the webapp calls `GET /api/openclaw/status` (backend runs `openclaw --version` via subprocess). If the CLI is not installed and the user has not dismissed the banner (`localStorage` key `openclaw-mcp-openclaw-install-dismissed`), **OpenClawInstallBanner** is shown above main content with install alternatives: naked (docs), Docker, VM (link to SECURITY.md). Dismiss hides it and sets the key.

## Logger modal and log server

The **Logger** button in the topbar opens a modal that shows:

- **Client logs**: App init, unhandled errors, and fetch failures (from the webapp).
- **Server logs**: MCP server log file (JSON lines) when a log server is running.

To see MCP server logs in the modal:

1. Run the MCP server at least once so it creates the log file (default: `~/.openclaw-mcp/logs/openclaw-mcp.log`).
2. Start the log server: `python -m openclaw_mcp.serve_logs` (default: http://127.0.0.1:8765).
3. In the Logger modal, set the URL to `http://127.0.0.1:8765/api/logs` (or leave default) and click **Refresh**.

Environment: `CLAWD_LOG_SERVER_PORT` (default 8765), `CLAWD_LOG_SERVER_HOST` (default 127.0.0.1). Webapp: `VITE_LOGS_API_URL` for default log API URL.

## Build

```bash
npm run build
```

Output: `webapp/dist/`

## Pages

- **Startpage**: Tool cards, **Ask OpenClaw** (message input → Gateway `/hooks/wake`), quick links
- **AI**: Ollama status, model list (pull/delete), quick prompt, shortcuts, chat (OpenClaw/Moltbook preprompt). Requires Ollama and webapp API.
- **Channels**: List channels, get channel config, send message, get recent messages. Proxies to Gateway tool `channels`. Requires Gateway to expose channels tool.
- **Routes**: View routing rules (channel → agent), update routing, test routing (dry-run), get session by channel. Proxies to Gateway tool `routing`; fallback: read from OpenClaw config.
- **Diagram**: Mermaid diagrams – OpenClaw system, openclaw-mcp and webapp connections, full system. Uses `mermaid` npm package.
- **Statistics**: Current snapshot (Gateway, routing topology) and placeholder for time-series (MCP calls, agents sent to Moltbook). Backend `/api/stats` or log aggregation planned.
- **Moltbook**: Prepare a Moltbook agent draft (name, bio, personality, goals, post ideas). Draft saved to localStorage; when OpenClaw is installed, **Register with Moltbook** sends the registration request to Moltbook (`POST /api/moltbook/register`). Links to Moltbook docs and skill.
- **Integrations**: Gateway status and installed skills (single source from OpenClaw; not duplication)
- **Clawnews**: Today’s media echo – curated OpenClaw/Moltbook news and docs
- **Generate**: Landing pages, OpenClaw env/config snippet, and MCP config snippet. **Landing page**: static site (hero, features, bio, download, donate, Ecosystem). Form: project name, hero title, subtitle, features, author, GitHub, donate, hero image keyword, include pictures. `POST /api/landing-page`; output in repo `generated/<slug>/www/`; preview at `http://localhost:5181/generated/<slug>/www/index.html`. **OpenClaw env snippet**: Gateway URL + optional token → .env.example and routing hint. **MCP config snippet**: insert openclaw-mcp into selected client configs (Cursor, Claude Desktop, Windsurf, Zed, Antigravity, LM Studio) with backup; Windsurf config at `%USERPROFILE%\.codeium\windsurf\mcp_config.json`. See [INSTALL.md](../INSTALL.md#mcp-client-config-locations).
- **Skills**, **Settings**: Placeholders / TBD
- **Security**: Security page intro, TBD audit/hardening; **Remove OpenClaw** section with steps (disconnect env, uninstall CLI, remove config) and link to [INSTALL.md#removing-openclaw](../INSTALL.md#removing-openclaw). MCP tool `clawd_openclaw_disconnect` returns same steps (no side effects).

## Ask OpenClaw

Uses the webapp API to proxy messages to OpenClaw Gateway. Same LLM OpenClaw uses (Ollama, Claude, etc.). Requires API and Gateway running.

## AI (Ollama)

The **AI** page proxies to local Ollama (default `http://localhost:11434`). Endpoints: `GET /api/ollama/health`, `GET /api/ollama/tags`, `POST /api/ollama/generate`, `POST /api/ollama/chat`, `POST /api/ollama/pull`, `DELETE /api/ollama/delete`. Chat uses system preprompt from `webapp_api/ollama_preprompt.txt`. Env: `OLLAMA_BASE` to override URL.

## Channels and Routes

- **Channels**: `POST /api/channels` with body `{ operation, channel?, to?, message?, limit?, session_key?, args? }`. Operations: `list_channels`, `get_channel_config`, `send_message`, `get_recent_messages`. Same as MCP tool `clawd_channels`.
- **Routes**: `POST /api/routing` with body `{ operation, channel?, agent?, peer?, body?, session_key?, args? }`. Operations: `get_routing_rules`, `update_routing`, `test_routing`, `get_session_by_channel`. Same as MCP tool `clawd_routing`. `get_routing_rules` falls back to OpenClaw config when Gateway does not expose the routing tool.

## Diagram, Statistics, Moltbook, Generate landing

- **Diagram**: Renders three Mermaid flowcharts (OpenClaw system; openclaw-mcp and webapp; full system). Uses `mermaid` (^11). Theme: dark. No API calls.
- **Statistics**: Fetches Gateway status and routing rules; shows current snapshot table and routing topology. Placeholder for time-series (MCP calls, agents sent to Moltbook) until `GET /api/stats` or log aggregation exists.
- **Moltbook**: Prepare-agent form (name, bio, personality, goals, post ideas). Draft saved to `localStorage` key `openclaw-mcp-moltbook-agent-draft`. When OpenClaw is installed, **Register with Moltbook** button sends `POST /api/moltbook/register` to register the agent with Moltbook (requires MOLTBOOK_API_KEY). Links to moltbook.com, skill.md, heartbeat.md.
- **Generate landing**: Form posts to `POST /api/landing-page`. Backend `webapp_api/landing_page_service.py` writes static site to repo `generated/<slug>/www/` (or `LANDING_PAGE_OUTPUT_DIR`): index, how_it_works, ecosystem, download, donate, bio, styles.css, script.js, plus `DEPLOY.md` in parent. Response includes `index_url`: `http://localhost:5181/generated/<slug>/www/index.html` (API serves `/generated` as static files for preview). Options: hero image keyword (default blue lobster), include pictures. Ecosystem page: OpenClaw, openclaw-mcp, Moltbook (descriptions + links), news/coverage, reviewers (Matthew Berman, Simon Willison, AI Explained). Page shows "How to get online" (GitHub Pages, Netlify, Vercel, Cloudflare Pages).

## Webapp API endpoints (summary)

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | API health |
| POST | /api/ask | Send message to OpenClaw (Gateway /hooks/wake) |
| GET | /api/gateway/status | Gateway reachability (sessions_list) |
| GET | /api/skills | List workspace skills |
| GET | /api/clawnews | Curated news items |
| GET | /api/ollama/health | Ollama reachable |
| GET | /api/ollama/tags | List Ollama models |
| POST | /api/ollama/generate | One-off generate |
| POST | /api/ollama/chat | Chat with history |
| POST | /api/ollama/pull | Pull model |
| DELETE | /api/ollama/delete | Delete model |
| POST | /api/channels | Channels operations (list, config, send, recent) |
| POST | /api/routing | Routing operations (rules, update, test, session) |
| GET | /api/openclaw/status | OpenClaw CLI installed (openclaw --version); returns cli_installed, version |
| POST | /api/landing-page | Generate static landing site (hero, features, ecosystem, DEPLOY.md); body: project_name, hero_title, hero_subtitle, features, github_url, author_name, author_bio, donate_link, hero_image_keyword, include_pictures. Returns index_url for preview. |
| GET | /api/mcp-config/clients | List MCP clients and config paths (for Generate page insert UI). |
| POST | /api/mcp-config/insert | Insert openclaw-mcp snippet into selected client configs; body: clients (array of client ids). Backs up originals; skips if already present. |
| POST | /api/moltbook/register | Register agent with Moltbook (POST /api/v1/agents/register); body: name, bio, personality, goals, ideas. Requires MOLTBOOK_API_KEY. |
