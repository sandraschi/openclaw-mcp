"""Tests for openclaw_mcp.config."""

import pytest

from openclaw_mcp.config import Settings


def test_settings_defaults() -> None:
    """Settings should have expected defaults."""
    s = Settings()
    assert s.gateway_url == "http://127.0.0.1:18789"
    assert s.gateway_token is None
    assert s.moltbook_api_key is None
    assert s.openclaw_path == "openclaw"
    assert s.workspace_path is None


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings should load from environment."""
    monkeypatch.setenv("OPENCLAW_GATEWAY_URL", "http://localhost:9999")
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "secret-token")
    monkeypatch.setenv("OPENCLAW_OPENCLAW_PATH", "openclaw-custom")
    s = Settings()
    assert s.gateway_url == "http://localhost:9999"
    assert s.gateway_token == "secret-token"
    assert s.openclaw_path == "openclaw-custom"


def test_settings_moltbook_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings should load MOLTBOOK_API_KEY from env."""
    monkeypatch.setenv("MOLTBOOK_API_KEY", "moltbook-secret")
    s = Settings()
    assert s.moltbook_api_key == "moltbook-secret"
