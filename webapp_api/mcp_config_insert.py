"""
Insert clawd-mcp snippet into MCP client config files. Creates backup before write.
Idempotent: skips if clawd-mcp key already present (no multi-insert).
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

SERVER_KEY = "clawd-mcp"

# Client id -> (config path relative to base, key path to mcpServers object as tuple)
# Base: APPDATA or USERPROFILE per client
CLIENT_PATHS: dict[str, tuple[str, str]] = {
    "cursor": ("Cursor/User/globalStorage/cursor-storage/mcp_config.json", "mcpServers"),
    "claude_desktop": ("Claude/claude_desktop_config.json", "mcpServers"),
    "windsurf": ("", "mcpServers"),  # USERPROFILE base below (.codeium/windsurf)
    "antigravity": ("", "mcpServers"),  # USERPROFILE base below
    "lm_studio": ("", "mcpServers"),  # USERPROFILE base below
    "zed": ("Zed/settings.json", "mcpServers"),
}
# Windsurf: USERPROFILE/.codeium/windsurf/mcp_config.json
# Antigravity: USERPROFILE/.gemini/antigravity/mcp_config.json
# LM Studio: USERPROFILE/.lmstudio/mcp.json

CLIENT_LABELS: dict[str, str] = {
    "cursor": "Cursor",
    "claude_desktop": "Claude Desktop",
    "windsurf": "Windsurf",
    "antigravity": "Antigravity",
    "lm_studio": "LM Studio",
    "zed": "Zed",
}


def _resolve_path(client_id: str) -> Path | None:
    if client_id == "windsurf":
        base = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        path = Path(base) / ".codeium" / "windsurf" / "mcp_config.json"
    elif client_id == "antigravity":
        base = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        path = Path(base) / ".gemini" / "antigravity" / "mcp_config.json"
    elif client_id == "lm_studio":
        base = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        path = Path(base) / ".lmstudio" / "mcp.json"
    else:
        base = os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming")
        rel, _ = CLIENT_PATHS.get(client_id, ("", ""))
        if not rel:
            return None
        path = Path(base) / rel
    return path


def _get_servers_key(client_id: str) -> str:
    return CLIENT_PATHS.get(client_id, ("", "mcpServers"))[1]


def list_clients() -> list[dict[str, Any]]:
    """Return list of { id, label, path, exists } for each known client."""
    result = []
    for cid in CLIENT_PATHS:
        path = _resolve_path(cid)
        result.append({
            "id": cid,
            "label": CLIENT_LABELS.get(cid, cid),
            "path": str(path) if path else None,
            "exists": path.exists() if path else False,
        })
    return result


def make_snippet(repo_root: Path) -> dict[str, Any]:
    root_str = repo_root.as_posix()
    return {
        "command": "python",
        "args": ["-m", "clawd_mcp"],
        "env": {
            "PYTHONPATH": f"{root_str}/src",
            "PYTHONUNBUFFERED": "1",
        },
    }


def insert_into_config(
    client_id: str,
    repo_root: Path,
) -> dict[str, Any]:
    """
    Read config, backup if needed, add clawd-mcp only if not present, write.
    Returns { "updated": bool, "skipped": bool, "backup_path": str | None, "error": str | None }.
    """
    path = _resolve_path(client_id)
    if not path or not path.parent.exists():
        return {"updated": False, "skipped": False, "backup_path": None, "error": "Config path not found"}
    if not path.exists():
        # Create parent and write new file with only clawd-mcp
        path.parent.mkdir(parents=True, exist_ok=True)
        servers_key = _get_servers_key(client_id)
        data: dict[str, Any] = {servers_key: {SERVER_KEY: make_snippet(repo_root)}}
        try:
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return {"updated": True, "skipped": False, "backup_path": None, "error": None}
        except OSError as e:
            return {"updated": False, "skipped": False, "backup_path": None, "error": str(e)}
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        return {"updated": False, "skipped": False, "backup_path": None, "error": str(e)}
    servers_key = _get_servers_key(client_id)
    servers = data.get(servers_key)
    if servers is None:
        data[servers_key] = {}
        servers = data[servers_key]
    if not isinstance(servers, dict):
        return {"updated": False, "skipped": False, "backup_path": None, "error": f"Unexpected structure: {servers_key} is not an object"}
    if SERVER_KEY in servers:
        return {"updated": False, "skipped": True, "backup_path": None, "error": None}
    backup_path = path.with_suffix(path.suffix + ".backup-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    try:
        backup_path.write_text(raw, encoding="utf-8")
    except OSError as e:
        return {"updated": False, "skipped": False, "backup_path": None, "error": f"Backup failed: {e}"}
    servers[SERVER_KEY] = make_snippet(repo_root)
    try:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"updated": True, "skipped": False, "backup_path": str(backup_path), "error": None}
    except OSError as e:
        return {"updated": False, "skipped": False, "backup_path": str(backup_path), "error": str(e)}
