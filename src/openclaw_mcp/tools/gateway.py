"""clawd_gateway: Gateway status and health."""

import asyncio
import logging
from typing import Literal

from fastmcp import Context

from openclaw_mcp.mcp_instance import mcp

from openclaw_mcp.gateway_client import GatewayClient
from openclaw_mcp.config import Settings

logger = logging.getLogger(__name__)


@mcp.tool()
async def clawd_gateway(
    ctx: Context,
    operation: Literal["status", "health", "doctor"] = "status",
) -> dict:
    """
    OpenClaw Gateway status and health operations.

    **Operations:**
    - `status`: Gateway status, bind, auth mode (via CLI).
    - `health`: Health check (via CLI).
    - `doctor`: Run doctor for migrations/config validation (via CLI).

    **Dialogic returns**: Natural language message plus structured data.

    Requires `openclaw` CLI on PATH and OPENCLAW_GATEWAY_URL reachable.
    """
    settings = Settings()
    client = GatewayClient(settings)

    try:
        if operation == "status":
            result = await client.tools_invoke(
                tool="sessions_list",
                action="json",
                args={},
            )
            if result.get("success"):
                return {
                    "success": True,
                    "message": "Gateway reachable. Tools Invoke API responded successfully.",
                    "data": result.get("data"),
                }
            return {
                "success": False,
                "message": "Gateway unreachable or Tools Invoke failed.",
                "error": result.get("error", str(result)),
            }

        if operation == "health":
            # Tools Invoke as health probe
            result = await client.tools_invoke(tool="sessions_list", args={})
            if result.get("success"):
                return {"success": True, "message": "Gateway healthy."}
            return {"success": False, "message": result.get("message", "Health check failed")}

        if operation == "doctor":
            # Run openclaw doctor via subprocess
            try:
                proc = await asyncio.create_subprocess_exec(
                    settings.openclaw_path,
                    "doctor",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                out = stdout.decode() if stdout else ""
                err = stderr.decode() if stderr else ""
                if proc.returncode == 0:
                    return {
                        "success": True,
                        "message": "Doctor completed successfully.",
                        "data": {"stdout": out, "stderr": err},
                    }
                return {
                    "success": False,
                    "message": f"Doctor exited with code {proc.returncode}",
                    "data": {"stdout": out, "stderr": err},
                }
            except FileNotFoundError as e:
                logger.warning(
                    "openclaw CLI not found: %s",
                    settings.openclaw_path,
                    extra={"tool": "clawd_gateway", "operation": "doctor", "error_type": "FileNotFoundError"},
                )
                return {
                    "success": False,
                    "message": f"openclaw CLI not found. Ensure '{settings.openclaw_path}' is on PATH.",
                    "error": str(e),
                }
            except Exception as e:
                logger.error(
                    "clawd_gateway doctor subprocess failed: %s",
                    e,
                    extra={"tool": "clawd_gateway", "operation": "doctor", "error_type": type(e).__name__},
                    exc_info=True,
                )
                return {
                    "success": False,
                    "message": f"Doctor subprocess failed: {e!s}",
                    "error": str(e),
                }

        return {"success": False, "message": f"Unknown operation: {operation}"}
    except Exception as e:
        logger.error(
            "clawd_gateway failed: %s",
            e,
            extra={"tool": "clawd_gateway", "operation": operation, "error_type": type(e).__name__},
            exc_info=True,
        )
        return {
            "success": False,
            "message": f"Gateway operation failed: {e!s}",
            "error": str(e),
        }
    finally:
        await client.close()
