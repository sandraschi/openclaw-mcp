"""Shared FastMCP instance for openclaw-mcp."""

from fastmcp import FastMCP

from openclaw_mcp import __version__

mcp = FastMCP(name="openclaw-mcp", version=__version__)
