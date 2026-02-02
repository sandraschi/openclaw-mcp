"""clawd_skills: Skills management and ClawHub."""

import logging
from pathlib import Path
from typing import Literal

from fastmcp import Context

from openclaw_mcp.mcp_instance import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def clawd_skills(
    ctx: Context,
    operation: Literal["list", "read"],
    skill_name: str | None = None,
    workspace_path: str | None = None,
) -> dict:
    """
    OpenClaw skills management.

    **Operations:**
    - `list`: List installed/eligible skills in workspace.
    - `read`: Read SKILL.md content for a skill.

    **Dialogic returns**: Natural language message plus structured data.

    Skills live in workspace/skills/ or ~/.openclaw/workspace/skills/.
    ClawHub (clawhub.com) is the public skills registry.
    """
    settings = Settings()
    base = Path(workspace_path) if workspace_path else Path.home() / ".openclaw" / "workspace"
    skills_dir = base / "skills"
    logger.info(
        "clawd_skills invoked",
        extra={"tool": "clawd_skills", "operation": operation},
    )

    try:
        if operation == "list":
            if not skills_dir.exists():
                return {
                    "success": True,
                    "message": "No workspace skills directory found. Run 'openclaw onboard' to set up.",
                    "data": {"skills": [], "path": str(skills_dir)},
                }
            skills = []
            for d in skills_dir.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists():
                    skills.append(d.name)
            return {
                "success": True,
                "message": f"Found {len(skills)} skills in workspace.",
                "data": {"skills": sorted(skills), "path": str(skills_dir)},
            }

        if operation == "read":
            if not skill_name:
                return {"success": False, "message": "skill_name required for read operation"}
            skill_path = skills_dir / skill_name / "SKILL.md"
            if not skill_path.exists():
                return {
                    "success": False,
                    "message": f"Skill '{skill_name}' not found.",
                    "data": {"path": str(skill_path)},
                }
            content = skill_path.read_text(encoding="utf-8")
            return {
                "success": True,
                "message": f"Read SKILL.md for '{skill_name}'.",
                "data": {"skill_name": skill_name, "content": content},
            }

        return {"success": False, "message": f"Unknown operation: {operation}"}
    except OSError as e:
        logger.error(
            "clawd_skills I/O failed: %s",
            e,
            extra={"tool": "clawd_skills", "operation": operation, "error_type": type(e).__name__},
            exc_info=True,
        )
        return {
            "success": False,
            "message": f"Skills I/O failed: {e!s}",
            "error": str(e),
        }
    except Exception as e:
        logger.error(
            "clawd_skills failed: %s",
            e,
            extra={"tool": "clawd_skills", "operation": operation, "error_type": type(e).__name__},
            exc_info=True,
        )
        return {
            "success": False,
            "message": f"Skills operation failed: {e!s}",
            "error": str(e),
        }
