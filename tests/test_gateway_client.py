"""Tests for openclaw_mcp.gateway_client."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from openclaw_mcp.config import Settings
from openclaw_mcp.gateway_client import GatewayClient


@pytest_asyncio.fixture
async def gateway_client(test_settings: Settings) -> GatewayClient:
    """GatewayClient with test settings."""
    return GatewayClient(test_settings)


@pytest.mark.asyncio
async def test_tools_invoke_success(gateway_client: GatewayClient) -> None:
    """tools_invoke should return dialogic success on ok response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"ok": True, "result": {"sessions": []}}

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_resp)

    with patch.object(
        gateway_client,
        "_get_client",
        new_callable=AsyncMock,
        return_value=mock_client,
    ):
        result = await gateway_client.tools_invoke("sessions_list", args={})
        assert result["success"] is True
        assert "message" in result
        assert result.get("data") == {"sessions": []}


@pytest.mark.asyncio
async def test_tools_invoke_not_ok(gateway_client: GatewayClient) -> None:
    """tools_invoke should return dialogic error when ok=False."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "ok": False,
        "error": {"message": "Tool not available"},
    }

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_resp)

    with patch.object(
        gateway_client,
        "_get_client",
        new_callable=AsyncMock,
        return_value=mock_client,
    ):
        result = await gateway_client.tools_invoke("sessions_list", args={})
        assert result["success"] is False
        assert "Tool not available" in result.get("message", "")
        assert "error" in result


@pytest.mark.asyncio
async def test_tools_invoke_http_error(gateway_client: GatewayClient) -> None:
    """tools_invoke should return dialogic error on HTTP status error."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unauthorized",
        request=MagicMock(),
        response=mock_resp,
    )

    with patch.object(
        gateway_client,
        "_get_client",
        return_value=MagicMock(post=AsyncMock(return_value=mock_resp)),
    ):
        result = await gateway_client.tools_invoke("sessions_list", args={})
        assert result["success"] is False
        assert "401" in result.get("message", "")


@pytest.mark.asyncio
async def test_tools_invoke_request_error(gateway_client: GatewayClient) -> None:
    """tools_invoke should return dialogic error on connection error."""
    mock_client = MagicMock()
    mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

    with patch.object(
        gateway_client,
        "_get_client",
        new_callable=AsyncMock,
        return_value=mock_client,
    ):
        result = await gateway_client.tools_invoke("sessions_list", args={})
        assert result["success"] is False
        assert "Gateway" in result.get("message", "")


@pytest.mark.asyncio
async def test_hooks_wake_success(gateway_client: GatewayClient) -> None:
    """hooks_wake should return dialogic success on 200."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_resp)

    with patch.object(
        gateway_client,
        "_get_client",
        new_callable=AsyncMock,
        return_value=mock_client,
    ):
        result = await gateway_client.hooks_wake("test message", mode="now")
        assert result["success"] is True
        assert "Wake triggered" in result.get("message", "")


@pytest.mark.asyncio
async def test_hooks_wake_http_error(gateway_client: GatewayClient) -> None:
    """hooks_wake should return dialogic error on HTTP error."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error",
        request=MagicMock(),
        response=mock_resp,
    )

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_resp)

    with patch.object(
        gateway_client,
        "_get_client",
        new_callable=AsyncMock,
        return_value=mock_client,
    ):
        result = await gateway_client.hooks_wake("test")
        assert result["success"] is False
        assert "500" in result.get("message", "")


@pytest.mark.asyncio
async def test_close(gateway_client: GatewayClient) -> None:
    """close should aclose the internal client."""
    mock_client = MagicMock(aclose=AsyncMock())
    gateway_client._client = mock_client

    await gateway_client.close()
    mock_client.aclose.assert_called_once()
    assert gateway_client._client is None
