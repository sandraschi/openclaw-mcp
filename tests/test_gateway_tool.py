"""Tests for clawd_gateway tool."""

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
async def test_clawd_gateway_status_success() -> None:
    """clawd_gateway status should return success when Tools Invoke succeeds."""
    with patch("openclaw_mcp.tools.gateway.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.tools_invoke = AsyncMock(
            return_value={"success": True, "data": {"sessions": []}}
        )
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client

        result = await mcp.call_tool(
            "clawd_gateway",
            arguments={"operation": "status"},
        )
        data = _extract_tool_result(result)
        assert data.get("success") is True
        assert "reachable" in data.get("message", "").lower()


@pytest.mark.asyncio
async def test_clawd_gateway_status_failure() -> None:
    """clawd_gateway status should return failure when Tools Invoke fails."""
    with patch("openclaw_mcp.tools.gateway.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.tools_invoke = AsyncMock(
            return_value={"success": False, "message": "Connection refused"}
        )
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client

        result = await mcp.call_tool(
            "clawd_gateway",
            arguments={"operation": "status"},
        )
        data = _extract_tool_result(result)
        assert data.get("success") is False
        assert "unreachable" in data.get("message", "").lower()


@pytest.mark.asyncio
async def test_clawd_gateway_health_success() -> None:
    """clawd_gateway health should return success when Tools Invoke succeeds."""
    with patch("openclaw_mcp.tools.gateway.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.tools_invoke = AsyncMock(return_value={"success": True})
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client

        result = await mcp.call_tool(
            "clawd_gateway",
            arguments={"operation": "health"},
        )
        data = _extract_tool_result(result)
        assert data.get("success") is True
        assert "healthy" in data.get("message", "").lower()


@pytest.mark.asyncio
async def test_clawd_gateway_doctor_success() -> None:
    """clawd_gateway doctor should run openclaw doctor subprocess."""
    with patch("openclaw_mcp.tools.gateway.asyncio.create_subprocess_exec") as mock_exec:
        mock_proc = MagicMock()
        mock_proc.communicate = AsyncMock(return_value=(b"stdout", b""))
        mock_proc.returncode = 0
        mock_exec.return_value = mock_proc

        result = await mcp.call_tool(
            "clawd_gateway",
            arguments={"operation": "doctor"},
        )
        data = _extract_tool_result(result)
        assert data.get("success") is True
        assert "doctor" in data.get("message", "").lower()
        mock_exec.assert_called_once()


@pytest.mark.asyncio
async def test_clawd_gateway_doctor_cli_not_found() -> None:
    """clawd_gateway doctor should return error when openclaw not found."""
    with patch("openclaw_mcp.tools.gateway.asyncio.create_subprocess_exec") as mock_exec:
        mock_exec.side_effect = FileNotFoundError("openclaw not found")

        result = await mcp.call_tool(
            "clawd_gateway",
            arguments={"operation": "doctor"},
        )
        data = _extract_tool_result(result)
        assert data.get("success") is False
        assert "not found" in data.get("message", "").lower()
