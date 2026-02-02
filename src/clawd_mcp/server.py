"""clawd-mcp FastMCP server entry point."""

import logging
import os
import sys

from clawd_mcp.config import Settings
from clawd_mcp.logging_config import setup_logging
from clawd_mcp.mcp_instance import mcp
from clawd_mcp.tools import agent, channels, gateway, moltbook, openclaw_remove, routing, security, sessions, skills  # noqa: F401 -- register tools

_settings = Settings()
setup_logging(_settings)
logger = logging.getLogger(__name__)

# Tools register via @mcp.tool() on import

# Optional: mount virtualization-mcp for sandbox provisioning (CLAWD_MOUNT_VBOX=1)
if os.environ.get("CLAWD_MOUNT_VBOX", "").lower() in ("1", "true", "yes"):
    try:
        from fastmcp.client import Client
        from fastmcp.client.transports import StdioTransport
        from fastmcp.server.proxy import FastMCPProxy

        def _vbox_client_factory():
            return Client(
                StdioTransport(
                    command=sys.executable,
                    args=["-m", "virtualization_mcp"],
                )
            )

        vbox_proxy = FastMCPProxy(
            client_factory=_vbox_client_factory,
            name="vbox",
        )
        mcp.mount(vbox_proxy, namespace="vbox")
        logger.info("virtualization-mcp mounted at vbox_*", extra={"tool": "server", "operation": "mount"})
    except Exception as e:
        logger.warning(
            "Could not mount virtualization-mcp: %s",
            e,
            exc_info=True,
            extra={"tool": "server", "operation": "mount", "error_type": type(e).__name__},
        )
