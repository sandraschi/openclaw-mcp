"""clawd_channels: OpenClaw channel visibility and messaging (WhatsApp, Telegram, Discord, etc.)."""

import logging
from pathlib import Path
from typing import Any, Literal

from fastmcp import Context

from openclaw_mcp.config import Settings
from openclaw_mcp.gateway_client import GatewayClient
from openclaw_mcp.mcp_instance import mcp

logger = logging.getLogger(__name__)

# Gateway tool/action mapping. When OpenClaw exposes channels via Tools Invoke, these are used.
CHANNELS_TOOL = "channels"
CHANNEL_ACTIONS = ("list_channels", "get_channel_config", "send_message", "get_recent_messages")


@mcp.tool()
async def clawd_channels(
    ctx: Context,
    operation: Literal["list_channels", "get_channel_config", "send_message", "get_recent_messages"],
    channel: str | None = None,
    to: str | None = None,
    message: str | None = None,
    limit: int = 20,
    session_key: str = "main",
    args: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    OpenClaw channel operations: list channels, config, send message, get recent messages.

    **Operations:**
    - `list_channels`: Enumerate active channels and connection status.
    - `get_channel_config`: Read channel-specific settings (allowFrom, routing rules).
    - `send_message`: Route a message to a channel (WhatsApp, Telegram, Discord, etc.).
    - `get_recent_messages`: Pull last N messages from a channel.

    **Args (by operation):**
    - list_channels: no extra args.
    - get_channel_config: `channel` (required).
    - send_message: `channel`, `to` (optional peer), `message` (required).
    - get_recent_messages: `channel`, `limit` (default 20).

    **Dialogic returns**: Natural language message plus structured data.

    Requires OpenClaw Gateway with Tools Invoke API. If the Gateway does not yet expose
    the channels tool, the call returns a clear error.
    """
    if operation not in CHANNEL_ACTIONS:
        return {
            "success": False,
            "message": f"Unknown operation: {operation}. Use one of: {', '.join(CHANNEL_ACTIONS)}",
        }

    if operation == "get_channel_config" and not (channel and channel.strip()):
        return {"success": False, "message": "get_channel_config requires 'channel'."}
    if operation == "send_message" and not (message and message.strip()):
        return {"success": False, "message": "send_message requires 'message'."}
    if operation == "get_recent_messages" and not (channel and channel.strip()):
        return {"success": False, "message": "get_recent_messages requires 'channel'."}

    settings = Settings()
    client = GatewayClient(settings)
    invoke_args: dict[str, Any] = dict(args or {})
    if channel:
        invoke_args["channel"] = channel.strip()
    if to:
        invoke_args["to"] = to.strip()
    if message:
        invoke_args["message"] = message.strip()
    if operation == "get_recent_messages":
        invoke_args["limit"] = max(1, min(limit, 100))

    try:
        result = await client.tools_invoke(
            tool=CHANNELS_TOOL,
            action=operation,
            args=invoke_args,
            session_key=session_key,
        )
        return result
    except Exception as e:
        logger.error(
            "clawd_channels failed: %s",
            e,
            extra={"tool": "clawd_channels", "operation": operation, "error_type": type(e).__name__},
            exc_info=True,
        )
        return {
            "success": False,
            "message": f"Channels operation failed: {e!s}",
            "error": str(e),
        }
    finally:
        await client.close()
