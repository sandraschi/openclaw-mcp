"""HTTP client for OpenClaw Gateway Tools Invoke and Webhooks API."""

import logging
from typing import Any

import httpx

from openclaw_mcp.config import Settings

logger = logging.getLogger(__name__)


def _dialogic_success(message: str, data: Any | None = None) -> dict[str, Any]:
    """Return dialogic success response (conversational + structured)."""
    result: dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        result["data"] = data
    return result


def _dialogic_error(message: str, error: str | None = None) -> dict[str, Any]:
    """Return dialogic error response."""
    result: dict[str, Any] = {"success": False, "message": message}
    if error:
        result["error"] = error
    return result


class GatewayClient:
    """Client for OpenClaw Gateway HTTP API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._client: httpx.AsyncClient | None = None

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.settings.gateway_token:
            headers["Authorization"] = f"Bearer {self.settings.gateway_token}"
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.settings.gateway_url,
                headers=self._headers(),
                timeout=30.0,
            )
        return self._client

    async def tools_invoke(
        self,
        tool: str,
        action: str | None = None,
        args: dict[str, Any] | None = None,
        session_key: str = "main",
    ) -> dict[str, Any]:
        """Invoke a Gateway tool via POST /tools/invoke."""
        body: dict[str, Any] = {"tool": tool, "args": args or {}, "sessionKey": session_key}
        if action:
            body["action"] = action

        try:
            client = await self._get_client()
            resp = await client.post("/tools/invoke", json=body)
            resp.raise_for_status()
            data = resp.json()
            if data.get("ok"):
                return _dialogic_success("Tool invoked successfully.", data.get("result"))
            return _dialogic_error(
                data.get("error", {}).get("message", "Tool invocation failed"),
                error=str(data.get("error", {})),
            )
        except httpx.HTTPStatusError as e:
            logger.error(
                "Gateway HTTP error: %s",
                e,
                extra={"tool": "gateway_client", "operation": "tools_invoke", "error_type": "HTTPStatusError"},
                exc_info=True,
            )
            return _dialogic_error(
                f"Gateway returned {e.response.status_code}",
                error=str(e),
            )
        except httpx.RequestError as e:
            logger.error(
                "Gateway request error: %s",
                e,
                extra={"tool": "gateway_client", "operation": "tools_invoke", "error_type": type(e).__name__},
                exc_info=True,
            )
            return _dialogic_error("Could not reach Gateway. Is OpenClaw running?", error=str(e))

    async def hooks_wake(self, text: str, mode: str = "now") -> dict[str, Any]:
        """Trigger wake via POST /hooks/wake."""
        try:
            client = await self._get_client()
            resp = await client.post("/hooks/wake", json={"text": text, "mode": mode})
            resp.raise_for_status()
            return _dialogic_success("Wake triggered successfully.")
        except httpx.HTTPStatusError as e:
            logger.error(
                "Wake HTTP error: %s",
                e,
                extra={"tool": "gateway_client", "operation": "hooks_wake", "error_type": "HTTPStatusError"},
                exc_info=True,
            )
            return _dialogic_error(f"Wake failed: {e.response.status_code}", error=str(e))
        except httpx.RequestError as e:
            logger.error(
                "Wake request error: %s",
                e,
                extra={"tool": "gateway_client", "operation": "hooks_wake", "error_type": type(e).__name__},
                exc_info=True,
            )
            return _dialogic_error("Could not reach Gateway.", error=str(e))

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
