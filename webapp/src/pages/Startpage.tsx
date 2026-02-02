import { useState } from "react";
import { Zap, MessageSquare, Layers, Settings2, Send } from "lucide-react";
import { cn } from "../utils/cn";
import { askOpenClaw } from "../services/api";
import { useLog } from "../context/LogContext";

const cards = [
  {
    title: "Agent",
    description: "Invoke OpenClaw agent, send messages, trigger wake",
    icon: Zap,
    tool: "clawd_agent",
  },
  {
    title: "Sessions",
    description: "List sessions, fetch history, agent-to-agent messaging",
    icon: MessageSquare,
    tool: "clawd_sessions",
  },
  {
    title: "Skills",
    description: "List and read OpenClaw workspace skills",
    icon: Layers,
    tool: "clawd_skills",
  },
  {
    title: "Gateway",
    description: "Status, health, doctor",
    icon: Settings2,
    tool: "clawd_gateway",
  },
];

export default function Startpage() {
  const [askInput, setAskInput] = useState("");
  const [askResponse, setAskResponse] = useState<string | null>(null);
  const [askLoading, setAskLoading] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);
  const { addLog } = useLog();

  async function handleAsk() {
    const msg = askInput.trim();
    if (!msg) return;
    setAskLoading(true);
    setAskError(null);
    setAskResponse(null);
    try {
      const res = await askOpenClaw(msg);
      setAskResponse(res.success ? res.message : res.error ?? res.message);
      if (!res.success) {
        addLog({
          ts: new Date().toISOString(),
          level: "WARNING",
          msg: `Ask OpenClaw: ${res.message}`,
          source: "client",
        });
      }
    } catch (err) {
      const text = err instanceof Error ? err.message : String(err);
      setAskError(text);
      addLog({
        ts: new Date().toISOString(),
        level: "ERROR",
        msg: `Ask OpenClaw failed: ${text}`,
        source: "client",
      });
    } finally {
      setAskLoading(false);
    }
  }

  return (
    <div className="space-y-10">
      <section
        className={cn(
          "relative overflow-hidden rounded-2xl border border-border",
          "bg-gradient-to-br from-card via-card to-card-accent/50",
          "px-8 py-12 sm:px-12 sm:py-16 md:px-16 md:py-20",
          "shadow-glow animate-fade-in"
        )}
      >
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-20%,rgba(249,115,22,0.12),transparent)]" aria-hidden />
        <div className="relative">
          <h1 className="font-mono text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl">
            openclaw-mcp
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-foreground-secondary sm:text-xl">
            Bridge Cursor and Claude Desktop to the OpenClaw and Moltbook ecosystem.
            Use MCP tools to invoke agents, manage sessions, and coordinate with Moltbook.
          </p>
          <p className="mt-2 text-sm text-foreground-tertiary">
            Gateway, channels, routes, skills, and Moltbook — one dashboard.
          </p>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-mono text-xl font-semibold text-foreground">
          Ask OpenClaw
        </h2>
        <p className="mt-1 text-sm text-foreground-secondary">
          Send a message to your OpenClaw agent (same LLM OpenClaw uses). Requires webapp API and Gateway running.
        </p>
        <div className="mt-4 flex gap-2">
          <input
            type="text"
            value={askInput}
            onChange={(e) => setAskInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder="Type a message..."
            className={cn(
              "flex-1 rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
              "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            )}
            disabled={askLoading}
          />
          <button
            type="button"
            onClick={handleAsk}
            disabled={askLoading || !askInput.trim()}
            className={cn(
              "rounded border border-primary bg-primary px-4 py-2 text-primary-foreground",
              "hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
            )}
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
        {askError && (
          <p className="mt-2 text-sm text-red-400">{askError}</p>
        )}
        {askResponse && (
          <p className="mt-2 rounded bg-muted p-3 text-sm text-foreground-secondary">
            {askResponse}
          </p>
        )}
      </section>

      <section className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map(({ title, description, icon: Icon, tool }) => (
          <div
            key={tool}
            className={cn(
              "rounded-lg border border-border bg-card p-6",
              "transition-colors hover:border-accent/50 hover:bg-card-accent/30",
              "shadow-glow-sm"
            )}
          >
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-md bg-primary/20 text-primary">
              <Icon className="h-5 w-5" />
            </div>
            <h2 className="font-mono text-lg font-semibold text-foreground">
              {title}
            </h2>
            <p className="mt-2 text-sm text-foreground-secondary">
              {description}
            </p>
            <code className="mt-3 block rounded bg-muted px-2 py-1 text-xs text-foreground-secondary">
              {tool}
            </code>
          </div>
        ))}
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-mono text-xl font-semibold text-foreground">
          Quick Links
        </h2>
        <ul className="mt-4 space-y-2 text-foreground-secondary">
          <li>
            <a
              href="https://openclaw.ai"
              target="_blank"
              rel="noreferrer"
              className="text-primary hover:underline"
            >
              openclaw.ai
            </a>{" "}
            - Personal AI assistant runtime
          </li>
          <li>
            <a
              href="https://moltbook.com"
              target="_blank"
              rel="noreferrer"
              className="text-primary hover:underline"
            >
              moltbook.com
            </a>{" "}
            - Social network for AI agents
          </li>
          <li>
            <a
              href="https://docs.openclaw.ai"
              target="_blank"
              rel="noreferrer"
              className="text-primary hover:underline"
            >
              docs.openclaw.ai
            </a>{" "}
            - OpenClaw documentation
          </li>
          <li>
            <a
              href="https://www.moltbook.com/heartbeat.md"
              target="_blank"
              rel="noreferrer"
              className="text-primary hover:underline"
            >
              moltbook.com/heartbeat.md
            </a>{" "}
            - Moltbook heartbeat pattern
          </li>
        </ul>
      </section>
    </div>
  );
}

