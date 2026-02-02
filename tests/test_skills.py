"""Tests for clawd_skills tool."""

import json
from pathlib import Path

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
async def test_clawd_skills_list_with_skills(
    mock_context: MagicMock,
    skills_workspace: Path,
) -> None:
    """clawd_skills list should return skills from workspace."""
    result = await clawd_skills(
        ctx=mock_context,
        operation="list",
        workspace_path=str(skills_workspace),
    )

    assert result["success"] is True
    assert "skill-a" in result.get("data", {}).get("skills", [])
    assert "skill-b" in result.get("data", {}).get("skills", [])


@pytest.mark.asyncio
async def test_clawd_skills_list_empty_dir(empty_skills_workspace: Path) -> None:
    """clawd_skills list with empty skills dir should return empty list."""
    result = await mcp.call_tool(
        "clawd_skills",
        arguments={"operation": "list", "workspace_path": str(empty_skills_workspace)},
    )
    data = _extract_tool_result(result)
    assert data.get("success") is True
    assert data.get("data", {}).get("skills", []) == []


@pytest.mark.asyncio
async def test_clawd_skills_list_no_dir(
    mock_context: MagicMock,
    no_skills_workspace: Path,
) -> None:
    """clawd_skills list with no skills dir should return onboarding hint."""
    result = await clawd_skills(
        ctx=mock_context,
        operation="list",
        workspace_path=str(no_skills_workspace),
    )

    assert result["success"] is True
    assert "onboard" in result.get("message", "").lower()


@pytest.mark.asyncio
async def test_clawd_skills_read_success(skills_workspace: Path) -> None:
    """clawd_skills read should return SKILL.md content."""
    result = await mcp.call_tool(
        "clawd_skills",
        arguments={
            "operation": "read",
            "skill_name": "skill-a",
            "workspace_path": str(skills_workspace),
        },
    )
    data = _extract_tool_result(result)
    assert data.get("success") is True
    assert "Skill A" in data.get("data", {}).get("content", "")


@pytest.mark.asyncio
async def test_clawd_skills_read_not_found(skills_workspace: Path) -> None:
    """clawd_skills read with unknown skill should return error."""
    result = await mcp.call_tool(
        "clawd_skills",
        arguments={
            "operation": "read",
            "skill_name": "nonexistent",
            "workspace_path": str(skills_workspace),
        },
    )
    data = _extract_tool_result(result)
    assert data.get("success") is False
    assert "not found" in data.get("message", "").lower()


@pytest.mark.asyncio
async def test_clawd_skills_read_missing_name() -> None:
    """clawd_skills read without skill_name should return error."""
    result = await mcp.call_tool(
        "clawd_skills",
        arguments={"operation": "read", "workspace_path": "/tmp"},
    )
    data = _extract_tool_result(result)
    assert data.get("success") is False
    assert "required" in data.get("message", "").lower()
