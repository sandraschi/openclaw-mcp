"""clawd_agent: Agent invocation and messaging (OpenClaw)."""

import logging
from typing import Literal

from fastmcp import Context

from openclaw_mcp.mcp_instance import mcp

from openclaw_mcp.gateway_client import GatewayClient
from openclaw_mcp.config import Settings

logger = logging.getLogger(__name__)


@mcp.tool()
async def clawd_agent(
    ctx: Context,
    operation: Literal["send_message", "run_agent", "wake"],
    message: str = "",
    session_key: str = "main",
    channel: Literal["last", "whatsapp", "telegram", "discord", "slack"] | None = None,
    to: str | None = None,
    deliver: bool = False,
    thinking: Literal["off", "minimal", "low", "medium", "high", "xhigh"] | None = None,
    timeout_seconds: int | None = None,
) -> dict:
    """
    Invoke OpenClaw agent operations.

    **Operations:**
    - `send_message`: Send message to agent; optionally deliver response to channel.
    - `run_agent`: Run isolated agent turn; return response to MCP (no channel delivery).
    - `wake`: Trigger heartbeat / wake main session with system event.

    **Dialogic returns**: Natural language message plus structured data.

    Requires OpenClaw Gateway running at OPENCLAW_GATEWAY_URL with OPENCLAW_GATEWAY_TOKEN
    when gateway auth is enabled. Webhooks require hooks.enabled and hooks.token in config.
    """
    settings = Settings()
    client = GatewayClient(settings)

    try:
        if operation == "wake":
            text = message or "Wake triggered via openclaw-mcp"
            result = await client.hooks_wake(text=text, mode="now")
            return result

        if operation == "run_agent":
            ctx.info("Running isolated agent turn (deliver=False)")
            # TODO: POST /hooks/agent with deliver=false
            return {
                "success": True,
                "message": "Agent run requested. Webhook /hooks/agent integration pending.",
                "data": {"operation": operation, "session_key": session_key},
            }

        if operation == "send_message":
            ctx.info("Sending message to agent")
            # TODO: POST /hooks/agent with deliver=deliver, channel, to
            return {
                "success": True,
                "message": "Message send requested. Webhook /hooks/agent integration pending.",
                "data": {"operation": operation, "deliver": deliver, "channel": channel},
            }

        return {
            "success": False,
            "message": f"Unknown operation: {operation}",
        }
    except Exception as e:
        logger.error(
            "clawd_agent failed: %s",
            e,
            extra={"tool": "clawd_agent", "operation": operation, "error_type": type(e).__name__},
            exc_info=True,
        )
        return {
            "success": False,
            "message": f"Agent operation failed: {e!s}",
            "error": str(e),
        }
    finally:
        await client.close()
