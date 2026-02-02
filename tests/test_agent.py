"""Tests for clawd_agent tool."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openclaw_mcp.mcp_instance import mcp


def _extract_tool_result(result: object) -> dict:
    """Extract dict from ToolResult (FastMCP serializes tool return to JSON)."""
    if hasattr(result, "content") and result.content:
        part = result.content[0]
        text = getattr(part, "text", str(part))
        if isinstance(text, str) and (text.startswith("{") or text.startswith("[")):
            return json.loads(text)
    return {}


@pytest.mark.asyncio
async def test_clawd_agent_wake() -> None:
    """clawd_agent wake operation should call hooks_wake."""
    with patch("openclaw_mcp.tools.agent.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.hooks_wake = AsyncMock(
            return_value={"success": True, "message": "Wake triggered successfully."}
        )
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client

        result = await mcp.call_tool(
            "clawd_agent",
            arguments={"operation": "wake", "message": "test wake"},
        )
        data = _extract_tool_result(result)
        assert data.get("success") is True
        assert "Wake" in data.get("message", "")
        mock_client.hooks_wake.assert_called_once_with(text="test wake", mode="now")


@pytest.mark.asyncio
async def test_clawd_agent_run_agent() -> None:
    """clawd_agent run_agent operation should return stub response."""
    with patch("openclaw_mcp.tools.agent.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client

        result = await mcp.call_tool(
            "clawd_agent",
            arguments={
                "operation": "run_agent",
                "message": "run this",
                "session_key": "main",
            },
        )
        data = _extract_tool_result(result)
        assert data.get("success") is True
        assert data.get("data", {}).get("operation") == "run_agent"


@pytest.mark.asyncio
async def test_clawd_agent_send_message() -> None:
    """clawd_agent send_message operation should return stub response."""
    with patch("openclaw_mcp.tools.agent.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client

        result = await mcp.call_tool(
            "clawd_agent",
            arguments={
                "operation": "send_message",
                "message": "hello",
                "deliver": True,
                "channel": "whatsapp",
            },
        )
        data = _extract_tool_result(result)
        assert data.get("success") is True
        assert data.get("data", {}).get("operation") == "send_message"
