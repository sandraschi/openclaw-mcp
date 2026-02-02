# clawd-mcp

[![Status](https://img.shields.io/badge/status-alpha-orange)](https://github.com/sandraschi/clawd-mcp)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-ecosystem-blue)](https://openclaw.ai)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.14+-blue)](https://github.com/jlowin/fastmcp)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**MCP server + webapp** that bridge Cursor and Claude Desktop to **OpenClaw** and **Moltbook**. clawd-mcp *uses* those platforms (Gateway, APIs); it does not implement or replace them. Alpha. Ingest for LLMs: [gitingest.com/sandraschi/clawd-mcp](https://gitingest.com/sandraschi/clawd-mcp).

## What this repo is

| Part | What it does |
|------|----------------|
| **MCP server** (stdio) | FastMCP 2.14+ tools: agent, sessions, channels, routing, skills, gateway, security, moltbook. For Cursor/Claude Desktop. |
| **Webapp** (React + Vite + Tailwind) | Dashboard on port 5180: Startpage, AI (Ollama), Channels, Routes, Diagram, Statistics, Moltbook, Integrations, Clawnews, Skills, Security, **Generate landing** (landing-site generator), Settings. |
| **webapp_api** (FastAPI) | Backend on 5181: /api/ask, /api/gateway/status, /api/skills, /api/clawnews, /api/ollama/*, /api/channels, /api/routing, /api/openclaw/status, /api/landing-page. |

One place to run agents, manage channels/routes/skills, and use Moltbook; OpenClaw and Moltbook stay separate.

## Install & run

**Clone-based** (no PyPI package yet). See **[INSTALL.md](INSTALL.md)** for: clone repo, install from source, MCP only or webapp (API + frontend), one-shot scripts, config, logging, checks.

## Repo layout

- **src/clawd_mcp/** – MCP server and tools
- **webapp/** – React dashboard (port 5180)
- **webapp_api/** – FastAPI backend (port 5181)
- **scripts/** – install.ps1, install.bat, start.ps1, start.bat, check.ps1, serve_logs.ps1

[Architecture](docs/ARCHITECTURE.md) – data flow, MCP vs API.

## Docs

| Doc | Description |
|-----|-------------|
| [INSTALL.md](INSTALL.md) | Install, run, config, checks |
| [docs/README_INDEX.md](docs/README_INDEX.md) | Doc index |
| [docs/README_WEBAPP.md](docs/README_WEBAPP.md) | Webapp pages, API, Logger |
| [docs/README_CLAWD_MCP_TOOLS.md](docs/README_CLAWD_MCP_TOOLS.md) | MCP tools |
| [docs/README_OPENCLAW.md](docs/README_OPENCLAW.md) | OpenClaw (external) |
| [docs/README_MOLTBOOK.md](docs/README_MOLTBOOK.md) | Moltbook (external) |
| [docs/HOW_THIS_WAS_MADE.md](docs/HOW_THIS_WAS_MADE.md) | How this was made (vibecode, Cursor, one day) |
| [SECURITY.md](SECURITY.md) | Threats, hardening |

## Security

OpenClaw has major security risks. Use **clawd_security**; prefer VM and loopback. [SECURITY.md](SECURITY.md), [docs/SECURITY_HARDENING.md](docs/SECURITY_HARDENING.md).

## Repo manifests (LLM scrapers)

| File | Triggers | Purpose |
|------|----------|---------|
| **glama.json** | [Glama](https://glama.ai) GitHub scraper | MCP server listing: claim ownership, metadata, Docker, usage. Requires `$schema` + `maintainers` (GitHub usernames). Re-run claim flow on Glama after changes. |
| **llms.txt** | [Gitingest](https://gitingest.com), [llmstxt.org](https://llmstxt.org) | LLM-friendly manifest: H1 + blockquote summary + ## sections with links. Improves repo ingestion for LLMs (e.g. `gitingest.com/sandraschi/clawd-mcp`). |

Other scrapers: no extra files needed. Gitingest ingests the repo (replace `github.com` with `gitingest.com` in the repo URL); llms.txt gives it a curated entry point. Glama is the main MCP-directory scraper that uses glama.json; others (e.g. Cursor’s MCP discovery) may crawl GitHub without a manifest.

## References

- [openclaw.ai](https://openclaw.ai) · [moltbook.com](https://moltbook.com) · [docs.openclaw.ai](https://docs.openclaw.ai)
- [mcp-central-docs/openclaw-moltbook](https://github.com/sandraschi/mcp-central-docs/tree/main/integrations/openclaw-moltbook)

---

*This README is formatted to render well on the GitHub repo page (pretty-printed).*
