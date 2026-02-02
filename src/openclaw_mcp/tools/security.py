"""clawd_security: OpenClaw hardening and audit operations."""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Literal

from fastmcp import Context

from openclaw_mcp.mcp_instance import mcp

from openclaw_mcp.config import Settings
from openclaw_mcp.gateway_client import GatewayClient

logger = logging.getLogger(__name__)

# Suspicious patterns in skills (backdoors, cred harvesting)
SKILL_RISK_PATTERNS = [
    (r"os\.environ|getenv|environ\.get", "high", "Accesses environment variables (may leak secrets)"),
    (r"open\([^)]*[\"']w[\"']|\.write\(", "medium", "File write capability"),
    (r"subprocess|exec|eval\s*\(", "high", "Command execution"),
    (r"requests\.(get|post)|httpx\.|urllib\.request", "medium", "Network outbound requests"),
    (r"\.ssh|id_rsa|private.?key", "critical", "SSH key access"),
    (r"token|api.?key|secret|password", "medium", "Potential secret handling"),
    (r"base64\.(b64decode|decode)", "medium", "Decoding (may obfuscate payload)"),
]

HARDENING_CHECKLIST = [
    {
        "id": "sandbox",
        "title": "Enable sandbox mode",
        "description": "Run OpenClaw in VM, container, or devbox. Restrict to one project directory.",
        "ref": "https://auth0.com/blog/five-step-guide-securing-moltbot-ai-agent/",
    },
    {
        "id": "bind_loopback",
        "title": "Bind gateway to loopback",
        "description": "Set gateway.bind to 127.0.0.1 (not 0.0.0.0) to prevent external access.",
        "ref": "https://docs.clawd.bot/security",
    },
    {
        "id": "allow_from",
        "title": "Restrict allowFrom list",
        "description": "Use allowFrom to whitelist which users/channels can talk to the bot.",
        "ref": "https://docs.clawd.bot/security",
    },
    {
        "id": "allow_lists",
        "title": "Enable command and path allow-lists",
        "description": "Allow-list commands, filesystem paths, integrations. Default-deny.",
        "ref": "https://auth0.com/blog/five-step-guide-securing-moltbot-ai-agent/",
    },
    {
        "id": "secrets",
        "title": "Scoped tokens and secret hygiene",
        "description": "Use scoped tokens, short-lived credentials. Never store secrets in .env agent can read.",
        "ref": "https://auth0.com/blog/five-step-guide-securing-moltbot-ai-agent/",
    },
    {
        "id": "skills_audit",
        "title": "Audit third-party skills",
        "description": "Malicious skills distributed via community can harvest creds. Verify source.",
        "ref": "https://www.intruder.io/blog/clawdbot-when-easy-ai-becomes-a-security-nightmare",
    },
    {
        "id": "prompt_injection",
        "title": "Prompt injection defense",
        "description": "Use model with injection defense. Test. Do not expose to untrusted social channels.",
        "ref": "https://auth0.com/blog/prompt-injection-ai-browser/",
    },
    {
        "id": "no_group_personal",
        "title": "Do not add personal bot to group chats",
        "description": "Personal bot knows your secrets. Use separate work bot for shared spaces.",
        "ref": "https://auth0.com/blog/five-step-guide-securing-moltbot-ai-agent/",
    },
]


@mcp.tool()
async def clawd_security(
    ctx: Context,
    operation: Literal["audit", "check_skills", "validate_config", "recommendations", "provision_sandbox"],
    workspace_path: str | None = None,
) -> dict:
    """
    OpenClaw security audit and hardening.

    **Operations:**
    - `audit`: Gateway bind, auth mode, token presence, doctor output.
    - `check_skills`: Scan workspace skills for suspicious patterns.
    - `validate_config`: Validate gateway.bind, allowFrom, missing secrets.
    - `recommendations`: Return hardening checklist (Auth0/Intruder).
    - `provision_sandbox`: Orchestration playbook for VM-based OpenClaw sandbox (virtualization-mcp).

    **Dialogic returns**: Natural language message plus structured data.

    References: Auth0, Intruder, docs.clawd.bot/security.
    """
    settings = Settings()
    base = Path(workspace_path) if workspace_path else Path.home() / ".openclaw" / "workspace"
    skills_dir = base / "skills"

    if operation == "audit":
        return await _audit(ctx, settings)

    if operation == "check_skills":
        return _check_skills(skills_dir)

    if operation == "validate_config":
        return await _validate_config(ctx, settings, base)

    if operation == "recommendations":
        return {
            "success": True,
            "message": f"Hardening checklist with {len(HARDENING_CHECKLIST)} items from Auth0 and Intruder.",
            "data": {"checklist": HARDENING_CHECKLIST},
        }

    if operation == "provision_sandbox":
        return _provision_sandbox_playbook()

    return {"success": False, "message": f"Unknown operation: {operation}"}


async def _audit(ctx: Context, settings: Settings) -> dict:
    """Audit gateway bind, auth, token, doctor."""
    findings: list[dict] = []
    client = GatewayClient(settings)
    try:
        result = await client.tools_invoke(tool="sessions_list", args={})
        if not result.get("success"):
            findings.append(
                {"id": "gateway_unreachable", "severity": "critical", "title": "Gateway unreachable"}
            )
        else:
            findings.append(
                {"id": "gateway_reachable", "severity": "info", "title": "Gateway reachable"}
            )
    except Exception as e:
        logger.error(
            "clawd_security audit gateway check failed: %s",
            e,
            extra={"tool": "clawd_security", "operation": "audit", "error_type": type(e).__name__},
            exc_info=True,
        )
        findings.append(
            {"id": "gateway_error", "severity": "critical", "title": f"Gateway error: {e}"}
        )
    finally:
        await client.close()

    if settings.gateway_token:
        findings.append({"id": "token_set", "severity": "info", "title": "Bearer token configured"})
    else:
        findings.append(
            {"id": "no_token", "severity": "medium", "title": "No OPENCLAW_GATEWAY_TOKEN set"}
        )

    url = settings.gateway_url
    if "0.0.0.0" in url or ":18789" in url and "127.0.0.1" not in url:
        findings.append(
            {"id": "bind_exposed", "severity": "high", "title": "Gateway may be bound to 0.0.0.0"}
        )
    elif "127.0.0.1" in url or "localhost" in url:
        findings.append({"id": "bind_loopback", "severity": "info", "title": "Gateway URL is loopback"})

    try:
        proc = await asyncio.create_subprocess_exec(
            settings.openclaw_path,
            "doctor",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        out = stdout.decode() if stdout else ""
        err = stderr.decode() if stderr else ""
        if proc.returncode == 0:
            findings.append({"id": "doctor_ok", "severity": "info", "title": "openclaw doctor passed"})
        else:
            findings.append(
                {
                    "id": "doctor_failed",
                    "severity": "high",
                    "title": f"openclaw doctor exited {proc.returncode}",
                    "details": out or err,
                }
            )
    except FileNotFoundError:
        findings.append({"id": "no_cli", "severity": "medium", "title": "openclaw CLI not found"})

    return {
        "success": True,
        "message": f"Audit complete. {len(findings)} findings.",
        "data": {"findings": findings},
    }


def _check_skills(skills_dir: Path) -> dict:
    """Scan skills for suspicious patterns."""
    if not skills_dir.exists():
        return {
            "success": True,
            "message": "No skills directory found. Nothing to scan.",
            "data": {"skills_checked": 0, "findings": []},
        }
    findings: list[dict] = []
    checked = 0
    for d in skills_dir.iterdir():
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            continue
        checked += 1
        content = skill_md.read_text(encoding="utf-8")
        for pattern, severity, desc in SKILL_RISK_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append(
                    {
                        "skill": d.name,
                        "severity": severity,
                        "description": desc,
                        "pattern": pattern,
                    }
                )
    return {
        "success": True,
        "message": f"Scanned {checked} skills. {len(findings)} potential risks.",
        "data": {"skills_checked": checked, "findings": findings},
    }


async def _validate_config(ctx: Context, settings: Settings, base: Path) -> dict:
    """Validate config files for common misconfigurations."""
    config_paths = [
        base / "clawdbot.json",
        base.parent / "clawdbot.json",
        Path.home() / ".openclaw" / "clawdbot.json",
    ]
    issues: list[dict] = []
    config_found = False
    for p in config_paths:
        if not p.exists():
            continue
        config_found = True
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            gateway = data.get("gateway") or {}
            bind = gateway.get("bind", "")
            if not bind or bind in ("0.0.0.0", "*"):
                issues.append({"path": str(p), "issue": "gateway.bind exposed (0.0.0.0 or missing)"})
            allow_from = gateway.get("allowFrom")
            if not allow_from:
                issues.append({"path": str(p), "issue": "gateway.allowFrom not configured"})
            tools_cfg = data.get("tools") or {}
            if not tools_cfg.get("allow") and not tools_cfg.get("safeBins"):
                issues.append({"path": str(p), "issue": "No tools allow-list or safeBins"})
        except json.JSONDecodeError as e:
            logger.warning(
                "Invalid JSON in config: %s",
                p,
                extra={"tool": "clawd_security", "operation": "validate_config", "error_type": "JSONDecodeError"},
            )
            issues.append({"path": str(p), "issue": f"Invalid JSON: {e}"})
    if not config_found:
        issues.append({"path": "none", "issue": "No clawdbot.json found in common locations"})
    return {
        "success": True,
        "message": f"Validated config. {len(issues)} issues.",
        "data": {"issues": issues, "paths_checked": [str(p) for p in config_paths]},
    }


def _provision_sandbox_playbook() -> dict:
    """Return orchestration playbook for VM-based OpenClaw sandbox via virtualization-mcp."""
    playbook = {
        "title": "OpenClaw sandbox provisioning via virtualization-mcp",
        "steps": [
            {
                "step": 1,
                "action": "Ensure virtualization-mcp is configured in your MCP client",
                "detail": "Add virtualization-mcp to Cursor/Claude config. Requires VirtualBox 7+.",
            },
            {
                "step": 2,
                "action": "Create VM using vm_management",
                "detail": "vm_management(action='create', vm_name='openclaw-sandbox', os_type='Ubuntu_64', memory_mb=4096, disk_size_gb=40)",
            },
            {
                "step": 3,
                "action": "Start VM and install OpenClaw inside",
                "detail": "vm_management(action='start', vm_name='openclaw-sandbox'). SSH/attach, run openclaw onboard.",
            },
            {
                "step": 4,
                "action": "Configure port forwarding (host 18789 -> guest 18789)",
                "detail": "network_management or VM settings to forward Gateway port.",
            },
            {
                "step": 5,
                "action": "Create snapshot after clean install",
                "detail": "snapshot_management(action='create', vm_name='openclaw-sandbox', snapshot_name='clean-install')",
            },
            {
                "step": 6,
                "action": "Point openclaw-mcp at forwarded host port",
                "detail": "OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789",
            },
        ],
        "compositing": "With both openclaw-mcp and virtualization-mcp in your MCP client, the LLM can execute these steps. clawd_security provision_sandbox returns this playbook.",
        "references": [
            "https://auth0.com/blog/five-step-guide-securing-moltbot-ai-agent/",
            "https://www.intruder.io/blog/clawdbot-when-easy-ai-becomes-a-security-nightmare",
        ],
    }
    return {
        "success": True,
        "message": "Sandbox provisioning playbook. Use with virtualization-mcp.",
        "data": playbook,
    }
