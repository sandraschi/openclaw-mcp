import { Shield } from "lucide-react";
import { cn } from "../utils/cn";

const INSTALL_REMOVING =
  "https://github.com/sandraschi/clawd-mcp/blob/main/INSTALL.md#removing-openclaw";

export default function Security() {
  return (
    <div className="space-y-10">
      <section>
        <h1 className="font-mono text-3xl font-bold text-foreground">
          Security
        </h1>
        <p className="mt-2 text-foreground-secondary">
          OpenClaw security audit and hardening. Audit, check skills, validate config, recommendations, sandbox provisioning.
        </p>
      </section>

      <section
        className={cn(
          "flex min-h-[200px] flex-col items-center justify-center rounded-lg border border-dashed border-border bg-card p-12",
          "text-center text-foreground-secondary"
        )}
      >
        <Shield className="mb-4 h-12 w-12 text-muted" />
        <p className="font-medium text-foreground">Security page</p>
        <p className="mt-2 text-sm">TBD: Run audit, view hardening checklist, provision sandbox.</p>
        <code className="mt-4 rounded bg-muted px-2 py-1 text-xs">clawd_security</code>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-mono text-xl font-semibold text-foreground">
          Remove OpenClaw
        </h2>
        <p className="mt-2 text-sm text-foreground-secondary">
          If you want to stop using OpenClaw or remove it (e.g. after security advisories or deciding it is not for you), clawd-mcp does not run uninstall for you. Follow the steps below to disconnect and optionally remove OpenClaw.
        </p>
        <ol className="mt-4 list-inside list-decimal space-y-2 text-sm text-foreground-secondary">
          <li>Stop the Gateway: quit any running OpenClaw process.</li>
          <li>
            Disconnect clawd-mcp: unset <code className="rounded bg-muted px-1">OPENCLAW_GATEWAY_URL</code> and{" "}
            <code className="rounded bg-muted px-1">OPENCLAW_GATEWAY_TOKEN</code> where you run the MCP server or webapp API; remove clawd-mcp from Cursor/Claude Desktop MCP config if you use it.
          </li>
          <li>Uninstall the CLI (optional): <code className="rounded bg-muted px-1">npm uninstall -g openclaw</code>; see OpenClaw docs if you used the install script.</li>
          <li>Remove config (optional): delete <code className="rounded bg-muted px-1">~/.openclaw</code>.</li>
        </ol>
        <a
          href={INSTALL_REMOVING}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 inline-block text-sm text-primary underline hover:no-underline"
        >
          Full steps: INSTALL.md – Removing OpenClaw
        </a>
        <p className="mt-2 text-xs text-muted">
          MCP tool: <code className="rounded bg-muted px-1">clawd_openclaw_disconnect</code> returns these steps and the doc link (no side effects).
        </p>
      </section>
    </div>
  );
}
