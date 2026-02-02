"""Tests for clawd_sessions tool."""

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
async def test_clawd_sessions_list_success() -> None:
    """clawd_sessions list should return success with sessions."""
    with patch("openclaw_mcp.tools.sessions.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.tools_invoke = AsyncMock(
            return_value={
                "success": True,
                "message": "Tool invoked successfully.",
                "data": {"sessions": [{"id": "main", "name": "Main"}]},
            }
        )
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client

        result = await mcp.call_tool(
            "clawd_sessions",
            arguments={"operation": "list", "session_key": "main"},
        )
        data = _extract_tool_result(result)
        assert data.get("success") is True
        mock_client.tools_invoke.assert_called_once_with(
            tool="sessions_list",
            action="json",
            args={},
            session_key="main",
        )


@pytest.mark.asyncio
async def test_clawd_sessions_history() -> None:
    """clawd_sessions history should invoke sessions_history."""
    with patch("openclaw_mcp.tools.sessions.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.tools_invoke = AsyncMock(
            return_value={"success": True, "data": {"messages": []}}
        )
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client

        result = await mcp.call_tool(
            "clawd_sessions",
            arguments={"operation": "history", "session_key": "main", "args": {"limit": 10}},
        )
        data = _extract_tool_result(result)
        assert data.get("success") is True
        mock_client.tools_invoke.assert_called_once_with(
            tool="sessions_history",
            action="json",
            args={"limit": 10},
            session_key="main",
        )
