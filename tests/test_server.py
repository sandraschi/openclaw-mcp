"""Basic server tests."""

import pytest

from openclaw_mcp.mcp_instance import mcp
from openclaw_mcp import __version__


def test_mcp_instance_exists() -> None:
    """MCP instance should exist."""
    assert mcp is not None


def test_mcp_version() -> None:
    """MCP version should be set."""
    assert __version__ == "0.1.0"


def test_mcp_has_name() -> None:
    """MCP instance should have name."""
    assert mcp.name == "openclaw-mcp"
