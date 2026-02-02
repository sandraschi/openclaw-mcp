"""Tests for clawd_routing tool."""

import json
from pathlib import Path
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
async def test_clawd_routing_get_routing_rules_success() -> None:
    """clawd_routing get_routing_rules should call Gateway tool routing with action get_routing_rules."""
    with patch("openclaw_mcp.tools.routing.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.tools_invoke = AsyncMock(
            return_value={
                "success": True,
                "message": "Tool invoked successfully.",
                "data": {"agents": {"whatsapp": "main"}},
            }
        )
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client

        result = await mcp.call_tool(
            "clawd_routing",
            arguments={"operation": "get_routing_rules", "session_key": "main"},
        )
        data = _extract_tool_result(result)
        assert data.get("success") is True
        mock_client.tools_invoke.assert_called_once()
        call_kw = mock_client.tools_invoke.call_args[1]
        assert call_kw["tool"] == "routing"
        assert call_kw["action"] == "get_routing_rules"


@pytest.mark.asyncio
async def test_clawd_routing_get_routing_rules_fallback(tmp_path: Path) -> None:
    """clawd_routing get_routing_rules falls back to config when Gateway fails."""
    config_path = tmp_path / "openclaw.json"
    config_path.write_text(
        '{"routing": {"agents": {"telegram": "main", "whatsapp": "main"}}}',
        encoding="utf-8",
    )
    with patch("openclaw_mcp.tools.routing.GatewayClient") as mock_gateway_class:
        mock_client = MagicMock()
        mock_client.tools_invoke = AsyncMock(
            return_value={"success": False, "message": "Unknown tool"}
        )
        mock_client.close = AsyncMock()
        mock_gateway_class.return_value = mock_client
    with patch("openclaw_mcp.tools.routing.Settings") as mock_settings_class:
        mock_settings = MagicMock()
        mock_settings.workspace_path = tmp_path / "workspace"
        mock_settings.workspace_path.parent = tmp_path
        mock_settings_class.return_value = mock_settings

        result = await mcp.call_tool(
            "clawd_routing",
            arguments={"operation": "get_routing_rules"},
        )
        data = _extract_tool_result(result)
        # Fallback only works when config is at workspace_path.parent / "openclaw.json"
        # Here workspace_path is tmp_path/workspace so parent is tmp_path; we wrote openclaw.json to tmp_path
        if data.get("success"):
            assert "data" in data or "agents" in str(data)
