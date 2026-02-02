"""HTTP client for Moltbook API (moltbook.com)."""

import logging
from typing import Any

import httpx

from openclaw_mcp.config import Settings

logger = logging.getLogger(__name__)

MOLTBOOK_BASE = "https://www.moltbook.com/api/v1"


def _dialogic_success(message: str, data: Any | None = None) -> dict[str, Any]:
    """Return dialogic success response."""
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


class MoltbookClient:
    """Client for Moltbook REST API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._client: httpx.AsyncClient | None = None

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.settings.moltbook_api_key:
            headers["Authorization"] = f"Bearer {self.settings.moltbook_api_key}"
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.settings.moltbook_url,
                headers=self._headers(),
                timeout=30.0,
            )
        return self._client

    async def get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        """GET request to Moltbook API."""
        try:
            client = await self._get_client()
            resp = await client.get(path, params=params)
            resp.raise_for_status()
            return _dialogic_success("OK", resp.json())
        except httpx.HTTPStatusError as e:
            logger.exception("Moltbook HTTP error: %s", e)
            return _dialogic_error(f"Moltbook returned {e.response.status_code}", error=str(e))
        except httpx.RequestError as e:
            logger.exception("Moltbook request error: %s", e)
            return _dialogic_error("Moltbook request failed", error=str(e))

    async def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """POST request to Moltbook API."""
        try:
            client = await self._get_client()
            resp = await client.post(path, json=json or {})
            resp.raise_for_status()
            data = resp.json() if resp.content else {}
            return _dialogic_success("OK", data)
        except httpx.HTTPStatusError as e:
            logger.error(
                "Moltbook HTTP error: %s",
                e,
                extra={"tool": "moltbook_client", "operation": "post", "error_type": "HTTPStatusError"},
                exc_info=True,
            )
            return _dialogic_error(f"Moltbook returned {e.response.status_code}", error=str(e))
        except httpx.RequestError as e:
            logger.error(
                "Moltbook request error: %s",
                e,
                extra={"tool": "moltbook_client", "operation": "post", "error_type": type(e).__name__},
                exc_info=True,
            )
            return _dialogic_error("Moltbook request failed", error=str(e))

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
