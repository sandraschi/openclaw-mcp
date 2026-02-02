"""Tests for clawd_channels tool."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openclaw_mcp.mcp_instance import mcp


def _extract_tool_result(result: object) -> dict:
    """Extract dict from ToolResult."""
    if hasattr(result, "content") and result.content:
        part = result.content[0]
        text = getattr(part, "text", str(part))
        if isinstance(text, str) and text.startswith("{"):
            return json.loads(text)
    return {}


@pytest.mark.asyncio
async def test_clawd_channels_list_channels_success() -> None:
    """clawd_channels list_channels should call Gateway tool channels with action list_channels."""
    with patch("openclaw_mcp.tools.channels.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.tools_invoke = AsyncMock(
            return_value={
                "success": True,
                "message": "Tool invoked successfully.",
                "data": {"channels": [{"name": "whatsapp", "connected": True}]},
            }
        )
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client

        result = await mcp.call_tool(
            "clawd_channels",
            arguments={"operation": "list_channels", "session_key": "main"},
        )
        data = _extract_tool_result(result)
        assert data.get("success") is True
        mock_client.tools_invoke.assert_called_once()
        call_kw = mock_client.tools_invoke.call_args[1]
        assert call_kw["tool"] == "channels"
        assert call_kw["action"] == "list_channels"


@pytest.mark.asyncio
async def test_clawd_channels_send_message_requires_message() -> None:
    """clawd_channels send_message without message returns error."""
    result = await mcp.call_tool(
        "clawd_channels",
        arguments={"operation": "send_message", "channel": "telegram"},
    )
    data = _extract_tool_result(result)
    assert data.get("success") is False
    assert "message" in (data.get("message") or "").lower()
