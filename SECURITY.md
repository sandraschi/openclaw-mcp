# Security

OpenClaw has major security risks (exposed credentials, prompt injection, malicious skills). **Run OpenClaw in a VM or container sandbox** when possible; bind the Gateway to loopback and use a reverse proxy (e.g. Traefik) for remote access with TLS and auth.

Use the **clawd_security** MCP tool for audit, skill scanning, config validation, and hardening. Set `CLAWD_MOUNT_VBOX=1` to use virtualization-mcp for VM provisioning.

**Full guide**: [docs/SECURITY_HARDENING.md](docs/SECURITY_HARDENING.md) – threats, hardening checklist, Tailscale/tailnet caveats (transitive trust, user beware), Traefik patterns, and security patterns.

**Removing OpenClaw**: [INSTALL.md#removing-openclaw](INSTALL.md#removing-openclaw) – steps to disconnect clawd-mcp and optionally uninstall OpenClaw. Webapp Security page and MCP tool `clawd_openclaw_disconnect` link there.

References: [Auth0 – Securing Moltbot](https://auth0.com/blog/five-step-guide-securing-moltbot-ai-agent/), [Intruder – Clawdbot Security Nightmare](https://www.intruder.io/blog/clawdbot-when-easy-ai-becomes-a-security-nightmare).
