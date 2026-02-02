"""clawd_routing: OpenClaw message routing topology (channels to agents)."""

import json
import logging
from pathlib import Path
from typing import Any, Literal

from fastmcp import Context

from openclaw_mcp.config import Settings
from openclaw_mcp.gateway_client import GatewayClient
from openclaw_mcp.mcp_instance import mcp

logger = logging.getLogger(__name__)

ROUTING_TOOL = "routing"
ROUTING_ACTIONS = ("get_routing_rules", "update_routing", "test_routing", "get_session_by_channel")


def _routing_config_fallback(settings: Settings) -> dict[str, Any] | None:
    """Read routing/agents from OpenClaw config if Gateway does not expose routing tool."""
    candidates: list[Path] = []
    if settings.workspace_path:
        # workspace is e.g. ~/.openclaw/workspace; config is ~/.openclaw/openclaw.json
        candidates.append(settings.workspace_path.resolve().parent / "openclaw.json")
    candidates.append(Path.home() / ".openclaw" / "openclaw.json")
    for path in candidates:
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                routing = data.get("routing") or {}
                agents = routing.get("agents") if isinstance(routing, dict) else None
                if agents is not None:
                    return {"agents": agents, "source": str(path)}
            except (json.JSONDecodeError, OSError) as e:
                logger.debug("Could not read routing from %s: %s", path, e)
    return None


@mcp.tool()
async def clawd_routing(
    ctx: Context,
    operation: Literal["get_routing_rules", "update_routing", "test_routing", "get_session_by_channel"],
    channel: str | None = None,
    agent: str | None = None,
    peer: str | None = None,
    body: str | None = None,
    session_key: str = "main",
    args: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    OpenClaw routing operations: rules, update, test, session lookup.

    **Operations:**
    - `get_routing_rules`: List which channels map to which agents (routing topology).
    - `update_routing`: Change channel-to-agent mappings (write; use with care).
    - `test_routing`: Simulate inbound message routing (dry-run).
    - `get_session_by_channel`: Find session from channel + peer.

    **Args (by operation):**
    - get_routing_rules: no extra args.
    - update_routing: `channel`, `agent` (required).
    - test_routing: `channel`, `peer`, `body` (optional; simulate inbound).
    - get_session_by_channel: `channel`, `peer` (required for lookup).

    **Dialogic returns**: Natural language message plus structured data.

    **Fallback:** If the Gateway does not expose the routing tool, get_routing_rules
    may return data read from OpenClaw config (~/.openclaw/openclaw.json) when present.

    Requires OpenClaw Gateway with Tools Invoke API.
    """
    if operation not in ROUTING_ACTIONS:
        return {
            "success": False,
            "message": f"Unknown operation: {operation}. Use one of: {', '.join(ROUTING_ACTIONS)}",
        }

    if operation == "update_routing":
        if not (channel and channel.strip()) or not (agent and agent.strip()):
            return {"success": False, "message": "update_routing requires 'channel' and 'agent'."}
        ctx.info("update_routing is a write operation; use with care")
    if operation == "get_session_by_channel" and not (channel and channel.strip()):
        return {"success": False, "message": "get_session_by_channel requires 'channel'."}

    settings = Settings()
    client = GatewayClient(settings)
    invoke_args: dict[str, Any] = dict(args or {})
    if channel:
        invoke_args["channel"] = channel.strip()
    if agent:
        invoke_args["agent"] = agent.strip()
    if peer:
        invoke_args["peer"] = peer.strip()
    if body is not None:
        invoke_args["body"] = body

    try:
        result = await client.tools_invoke(
            tool=ROUTING_TOOL,
            action=operation,
            args=invoke_args,
            session_key=session_key,
        )
        # Fallback for get_routing_rules when Gateway does not support routing tool
        if operation == "get_routing_rules" and not result.get("success"):
            fallback = _routing_config_fallback(settings)
            if fallback:
                return {
                    "success": True,
                    "message": "Routing rules from OpenClaw config (Gateway routing tool not available).",
                    "data": fallback,
                }
        return result
    except Exception as e:
        logger.error(
            "clawd_routing failed: %s",
            e,
            extra={"tool": "clawd_routing", "operation": operation, "error_type": type(e).__name__},
            exc_info=True,
        )
        return {
            "success": False,
            "message": f"Routing operation failed: {e!s}",
            "error": str(e),
        }
    finally:
        await client.close()
