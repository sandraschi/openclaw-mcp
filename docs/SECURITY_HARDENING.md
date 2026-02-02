# Security – OpenClaw and openclaw-mcp

OpenClaw (formerly Moltbot/Clawdbot) has major security risks when run with default configuration. This document summarizes threats, hardening steps, network patterns (Tailscale, Traefik), and openclaw-mcp security tools.

**Quick link**: [clawd_security tool](#openclaw-mcp-security-tools) | [Hardening checklist](#hardening-checklist-auth0-intruder) | [Network patterns](#network-patterns-tailscale-traefik) | [Security patterns](#security-patterns) | [Removing OpenClaw](../INSTALL.md#removing-openclaw)

---

## Summary (from main README)

OpenClaw exposes credentials, prompt injection, and malicious skills risks. Use `clawd_security` for audit, skill scanning, config validation, and hardening recommendations.

**Recommended: run OpenClaw in a VirtualBox (or other VM) sandbox** so the agent and tools are isolated from your host. Use `clawd_security` with `operation: "provision_sandbox"` for a playbook; set `CLAWD_MOUNT_VBOX=1` to mount virtualization-mcp and provision the VM via MCP.

References: [Auth0 – Securing Moltbot](https://auth0.com/blog/five-step-guide-securing-moltbot-ai-agent/), [Intruder – Clawdbot Security Nightmare](https://www.intruder.io/blog/clawdbot-when-easy-ai-becomes-a-security-nightmare).

---

## Active Threats (Intruder, Jan 2026)

- **Exposed credentials**: Misconfigurations expose API keys, tokens, entire config files
- **Prompt injection**: Social media integrations leak private data via crafted prompts
- **Malicious skills**: Backdoored plugins via community channels (credential harvesting, botnet recruitment)
- **Configuration corruption**: Non-atomic writes allow agents to overwrite clawdbot.json, remove gateway.mode

## Architectural Vulnerabilities

- **No sandbox by default**: Agent has full access to file system, shell, SSH keys, email
- **Missing validation**: Boot-critical settings not validated before disk write
- **Insufficient guardrails**: Unauthorized posting, data exfiltration, command execution beyond intent

---

## Hardening Checklist (Auth0, Intruder)

1. **Enable sandbox mode** – Run OpenClaw in VM, container, or devbox. Restrict to one project directory.
2. **Bind gateway to loopback** – Set `gateway.bind` to `127.0.0.1` (not `0.0.0.0`).
3. **Restrict allowFrom** – Whitelist which users/channels can talk to the bot.
4. **Enable allow-lists** – Command allow-list, filesystem allow-list, integration allow-list. Default-deny.
5. **Scoped tokens and secrets** – Use scoped tokens, short-lived credentials. Never store secrets in .env the agent can read.
6. **Audit third-party skills** – Verify source. Malicious skills harvest creds.
7. **Prompt injection defense** – Use model with injection defense. Do not expose to untrusted social channels.
8. **Do not add personal bot to group chats** – Use separate work bot for shared spaces.

---

## Network Patterns: Tailscale, Traefik

### Tailscale / Tailnet

**Tailscale** (and tailnets) can expose the Gateway or webapp to other devices without opening ports on the public internet. Useful for remote access from a phone or another machine on the same tailnet.

- **Transitive trust**: Devices on the same tailnet are trusted by Tailscale’s ACLs. A compromised or overly permissive device can reach your OpenClaw Gateway if you advertise it. **User beware**: treat the tailnet as a soft trust boundary, not a hard security boundary.
- **Recommendation**: Only advertise the Gateway (or openclaw-mcp webapp) to the tailnet if you trust every device and user on that tailnet. Prefer binding to loopback and using Tailscale only for outbound (e.g. agent reaching external APIs), or use an explicit allow-list for which tailnet nodes can connect.
- **Docs**: [Tailscale – Serve](https://tailscale.com/kb/1247/serve), [ACLs](https://tailscale.com/kb/1018/acls).

### Traefik (and reverse proxies)

**Traefik** (or Caddy, nginx, etc.) in front of the Gateway or webapp gives:

- **TLS termination** – HTTPS in, HTTP to backend; no plaintext on the wire.
- **Auth** – Basic auth, OIDC, or API keys at the edge so the Gateway itself can stay loopback-only.
- **Rate limiting and WAF** – Limit requests per IP, block common attacks before they hit OpenClaw.
- **Path-based routing** – Expose only `/api/ask` or specific paths; hide admin or debug endpoints.

**Pattern**: Bind OpenClaw Gateway to `127.0.0.1:18789`. Run Traefik on the host (or in a container) with a single frontend that proxies to `http://127.0.0.1:18789`. Put TLS and auth on Traefik; keep the Gateway off the public interface.

---

## Security Patterns

Patterns that fit well with OpenClaw and openclaw-mcp:

1. **Loopback-first, proxy for access**  
   Gateway and webapp API bind to `127.0.0.1`. Any remote or LAN access goes through a reverse proxy (Traefik, Caddy) with TLS and auth. No direct exposure of OpenClaw ports.

2. **VM or container sandbox**  
   Run OpenClaw (and optionally openclaw-mcp) inside a VM or container. Host only runs the reverse proxy and MCP client; the agent’s blast radius is limited to the sandbox.

3. **Scoped tokens**  
   Use a dedicated token for openclaw-mcp and Gateway; rotate it. Do not reuse the same token for CI, webhooks, and human access. Prefer short-lived tokens where the stack supports it.

4. **Skills allow-list**  
   Install only skills from trusted sources. Use `clawd_security` → `check_skills` regularly. Prefer a curated list (e.g. internal ClawHub fork) over public installs.

5. **Channel segregation**  
   Use one bot/instance for personal channels and another for group or work channels. Restrict `allowFrom` per channel so a compromise in one channel does not imply access to all.

6. **Audit trail**  
   Log Gateway access and MCP tool calls (openclaw-mcp structured logs, Traefik access logs). Retain for incident review; avoid logging full message bodies or secrets.

7. **No secrets in agent-visible config**  
   Keep API keys and tokens in env vars or a secret manager the agent cannot read. Validate config with `clawd_security` → `validate_config` before deploy.

8. **Tailnet as soft boundary**  
   If using Tailscale to reach the Gateway, treat the tailnet as “trusted but verify”: limit which nodes can connect, and assume one compromised tailnet device could try to reach the Gateway.

---

## openclaw-mcp Security Tools

Use `clawd_security` for:

| Operation | Description |
|-----------|-------------|
| **audit** | Gateway bind, auth mode, token presence, openclaw doctor |
| **check_skills** | Scan workspace skills for suspicious patterns |
| **validate_config** | Validate gateway.bind, allowFrom, tools.allow |
| **recommendations** | Return full hardening checklist |
| **provision_sandbox** | Orchestration playbook for VM-based sandbox (virtualization-mcp) |

Set `CLAWD_MOUNT_VBOX=1` to mount virtualization-mcp at `vbox_*` for VM provisioning.

---

## References

- [Auth0: Securing OpenClaw – Five-Step Checklist](https://auth0.com/blog/five-step-guide-securing-moltbot-ai-agent/)
- [Intruder: Clawdbot Security Nightmare](https://www.intruder.io/blog/clawdbot-when-easy-ai-becomes-a-security-nightmare)
- [docs.clawd.bot – Security](https://docs.clawd.bot/security)
- [Tailscale – Serve](https://tailscale.com/kb/1247/serve) | [ACLs](https://tailscale.com/kb/1018/acls)
- [Traefik – Overview](https://doc.traefik.io/traefik/)
