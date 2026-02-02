"""clawd_openclaw_disconnect: Disconnect from OpenClaw and get removal steps."""

import logging
from textwrap import dedent

from fastmcp import Context

from clawd_mcp.mcp_instance import mcp

logger = logging.getLogger(__name__)

REMOVAL_STEPS = dedent("""
    1. Stop the Gateway: quit any running OpenClaw process (Gateway, Pi agent).
    2. Disconnect clawd-mcp:
       - MCP: Remove clawd-mcp from Cursor/Claude Desktop MCP config. Unset OPENCLAW_GATEWAY_URL and OPENCLAW_GATEWAY_TOKEN in the environment that starts the MCP server.
       - Webapp API: Unset OPENCLAW_GATEWAY_URL and OPENCLAW_GATEWAY_TOKEN where you run uvicorn; restart the API.
    3. Uninstall OpenClaw CLI (optional): npm uninstall -g openclaw; or see OpenClaw docs if you used the install script.
    4. Remove config (optional): delete ~/.openclaw to wipe Gateway config and local data.

    Full steps: INSTALL.md section "Removing OpenClaw" in the clawd-mcp repo.
""").strip()


@mcp.tool()
async def clawd_openclaw_disconnect(ctx: Context) -> dict:
    """
    Get steps to disconnect clawd-mcp from OpenClaw and optionally remove OpenClaw.

    Use this if you want to stop using OpenClaw (e.g. after security advisories
    or deciding it is not for you). This tool does not change any config or
    run uninstall; it returns instructions only.

    **Returns**: Message with steps to disconnect (unset env, remove from MCP
    config), optional uninstall of OpenClaw CLI, and optional removal of
    ~/.openclaw. Link to INSTALL.md "Removing OpenClaw" in the repo.
    """
    logger.info(
        "clawd_openclaw_disconnect called",
        extra={"tool": "clawd_openclaw_disconnect"},
    )
    doc_url = "https://github.com/sandraschi/clawd-mcp/blob/main/INSTALL.md#removing-openclaw"
    return {
        "success": True,
        "message": "Disconnect and removal steps (no changes made by this tool):",
        "data": {
            "steps": REMOVAL_STEPS,
            "doc_url": doc_url,
        },
    }
