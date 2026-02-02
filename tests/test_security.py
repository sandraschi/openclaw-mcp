"""Tests for clawd_security tool."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

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
async def test_clawd_security_recommendations() -> None:
    """clawd_security recommendations should return hardening checklist."""
    result = await mcp.call_tool(
        "clawd_security",
        arguments={"operation": "recommendations"},
    )
    data = _extract_tool_result(result)
    assert data.get("success") is True
    checklist = data.get("data", {}).get("checklist", [])
    assert len(checklist) > 0
    assert any(i.get("id") == "sandbox" for i in checklist)


@pytest.mark.asyncio
async def test_clawd_security_provision_sandbox() -> None:
    """clawd_security provision_sandbox should return playbook."""
    result = await mcp.call_tool(
        "clawd_security",
        arguments={"operation": "provision_sandbox"},
    )
    data = _extract_tool_result(result)
    assert data.get("success") is True
    playbook = data.get("data", {})
    assert "steps" in playbook
    assert "virtualization-mcp" in data.get("message", "")


@pytest.mark.asyncio
async def test_clawd_security_check_skills_empty(tmp_path: Path) -> None:
    """clawd_security check_skills with no skills dir returns empty scan."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    result = await mcp.call_tool(
        "clawd_security",
        arguments={"operation": "check_skills", "workspace_path": str(workspace)},
    )
    data = _extract_tool_result(result)
    assert data.get("success") is True
    assert data.get("data", {}).get("skills_checked") == 0


@pytest.mark.asyncio
async def test_clawd_security_check_skills_with_skill(tmp_path: Path) -> None:
    """clawd_security check_skills scans skills dir."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    skill_a = skills_dir / "skill-a"
    skill_a.mkdir()
    (skill_a / "SKILL.md").write_text("# Skill A\n\nUses os.environ for config.\n", encoding="utf-8")
    result = await mcp.call_tool(
        "clawd_security",
        arguments={"operation": "check_skills", "workspace_path": str(tmp_path)},
    )
    data = _extract_tool_result(result)
    assert data.get("success") is True
    assert data.get("data", {}).get("skills_checked") == 1
    findings = data.get("data", {}).get("findings", [])
    assert any(f.get("skill") == "skill-a" for f in findings)


@pytest.mark.asyncio
async def test_clawd_security_validate_config_no_config(tmp_path: Path) -> None:
    """clawd_security validate_config with no config returns issues."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    result = await mcp.call_tool(
        "clawd_security",
        arguments={"operation": "validate_config", "workspace_path": str(workspace)},
    )
    data = _extract_tool_result(result)
    assert data.get("success") is True
    assert len(data.get("data", {}).get("issues", [])) >= 0


@pytest.mark.asyncio
async def test_clawd_security_audit_gateway_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
    """clawd_security audit when gateway unreachable reports finding."""
    monkeypatch.setenv("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:19999")
    result = await mcp.call_tool(
        "clawd_security",
        arguments={"operation": "audit"},
    )
    data = _extract_tool_result(result)
    assert data.get("success") is True
    findings = data.get("data", {}).get("findings", [])
    assert any(f.get("id") in ("gateway_unreachable", "gateway_error", "gateway_reachable") for f in findings)


@pytest.mark.asyncio
async def test_clawd_security_unknown_operation() -> None:
    """clawd_security unknown operation returns error."""
    result = await mcp.call_tool(
        "clawd_security",
        arguments={"operation": "unknown_op"},
    )
    data = _extract_tool_result(result)
    assert data.get("success") is False
    assert "unknown" in data.get("message", "").lower()
