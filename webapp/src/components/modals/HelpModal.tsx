import { useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "../../utils/cn";

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function HelpModal({ isOpen, onClose }: HelpModalProps) {
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="help-title"
    >
      <div
        className={cn(
          "mx-4 max-h-[85vh] w-full max-w-xl overflow-y-auto rounded-lg border border-border",
          "bg-background-secondary shadow-glow animate-fade-in"
        )}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h2 id="help-title" className="font-mono text-lg font-semibold text-foreground">
            Help
          </h2>
          <button
            type="button"
            onClick={onClose}
            className={cn(
              "rounded-md p-2 text-foreground-secondary transition-colors",
              "hover:bg-muted hover:text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
            )}
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="space-y-4 px-6 py-4 text-sm text-foreground-secondary">
          <p>
            <strong className="text-foreground">openclaw-mcp</strong> bridges Cursor
            and Claude Desktop with the OpenClaw and Moltbook ecosystem.
          </p>
          <section>
            <h3 className="mb-2 font-medium text-foreground">MCP Tools</h3>
            <ul className="list-inside list-disc space-y-1">
              <li><code className="rounded bg-muted px-1.5 py-0.5">clawd_agent</code> – Invoke agent, wake, send messages</li>
              <li><code className="rounded bg-muted px-1.5 py-0.5">clawd_sessions</code> – List sessions, history, agent messaging</li>
              <li><code className="rounded bg-muted px-1.5 py-0.5">clawd_skills</code> – List and read skills</li>
              <li><code className="rounded bg-muted px-1.5 py-0.5">clawd_gateway</code> – Status, health, doctor</li>
              <li><code className="rounded bg-muted px-1.5 py-0.5">clawd_security</code> – Audit, hardening, sandbox</li>
              <li><code className="rounded bg-muted px-1.5 py-0.5">clawd_moltbook</code> – Feed, post, comment, heartbeat</li>
            </ul>
          </section>
          <section>
            <h3 className="mb-2 font-medium text-foreground">How this was made</h3>
            <p className="mb-2">
              Planned by vibecode architect sandraschi, in beautiful Vienna (Alsergrund); implementation by Cursor (agentic IDE) with various LLMs. Scaffold, implement, test harness, debug, iterate. One day, token cost zilch. If you are an AI-luddite or butlerite, feel free to hate on it.
            </p>
            <p className="mb-2">
              <a href="https://github.com/sandraschi/openclaw-mcp/blob/main/docs/HOW_THIS_WAS_MADE.md" target="_blank" rel="noreferrer" className="text-primary hover:underline">
                docs/HOW_THIS_WAS_MADE.md
              </a>
            </p>
          </section>
          <section>
            <h3 className="mb-2 font-medium text-foreground">Links</h3>
            <ul className="space-y-1">
              <li>
                <a href="https://openclaw.ai" target="_blank" rel="noreferrer" className="text-primary hover:underline">
                  openclaw.ai
                </a>
              </li>
              <li>
                <a href="https://moltbook.com" target="_blank" rel="noreferrer" className="text-primary hover:underline">
                  moltbook.com
                </a>
              </li>
              <li>
                <a href="https://docs.openclaw.ai" target="_blank" rel="noreferrer" className="text-primary hover:underline">
                  docs.openclaw.ai
                </a>
              </li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
}

