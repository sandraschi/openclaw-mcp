# openclaw-mcp Webapp API

FastAPI backend for the webapp: proxy to OpenClaw Gateway (Ask), gateway status, skills list, clawnews.

## Run

From repo root with `PYTHONPATH=src` so `openclaw_mcp` is importable:

```powershell
# Install optional deps
pip install -e ".[webapp-api]"

# Run (from repo root)
$env:PYTHONPATH = "src"
uvicorn webapp_api.main:app --reload --port 5181
```

Port **5181**. The webapp (Vite dev) proxies `/api` to this server.

## Endpoints

- `GET /api/health` – health check
- `POST /api/ask` – body `{ "message": "..." }` → forwards to OpenClaw Gateway `/hooks/wake`
- `GET /api/gateway/status` – Gateway reachability and sessions_list
- `GET /api/skills` – list OpenClaw workspace skills (same source as clawd_skills)
- `GET /api/clawnews` – curated OpenClaw/Moltbook news and docs

Uses `OPENCLAW_GATEWAY_URL`, `OPENCLAW_GATEWAY_TOKEN`, `OPENCLAW_WORKSPACE` (optional) from env or `.env`.
