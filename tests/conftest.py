"""Pytest configuration and fixtures for openclaw-mcp."""

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from openclaw_mcp.config import Settings


@pytest.fixture
def project_root() -> Path:
    """Project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def test_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Settings with test gateway URL."""
    monkeypatch.setenv("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:18789")
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "")
    return Settings()


@pytest.fixture
def settings_with_token(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Settings with gateway token."""
    monkeypatch.setenv("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:18789")
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "test-token-123")
    return Settings()


@pytest.fixture
def mock_context() -> MagicMock:
    """Mock FastMCP Context for tool tests."""
    ctx = MagicMock()
    ctx.info = MagicMock()
    ctx.report_progress = MagicMock()
    return ctx


@pytest.fixture
def skills_workspace(tmp_path: Path) -> Path:
    """Temporary workspace with skills directory and sample SKILL.md."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    skill_a = skills_dir / "skill-a"
    skill_a.mkdir()
    (skill_a / "SKILL.md").write_text("# Skill A\n\nContent for skill A.", encoding="utf-8")

    skill_b = skills_dir / "skill-b"
    skill_b.mkdir()
    (skill_b / "SKILL.md").write_text("# Skill B\n\nContent for skill B.", encoding="utf-8")

    return tmp_path


@pytest.fixture
def empty_skills_workspace(tmp_path: Path) -> Path:
    """Temporary workspace with empty skills directory."""
    (tmp_path / "skills").mkdir()
    return tmp_path


@pytest.fixture
def no_skills_workspace(tmp_path: Path) -> Path:
    """Temporary workspace without skills directory."""
    return tmp_path


@pytest_asyncio.fixture
async def mock_httpx_client() -> AsyncMock:
    """Mock httpx.AsyncClient for GatewayClient tests."""
    client = AsyncMock()
    client.post = AsyncMock()
    client.aclose = AsyncMock()
    return client
