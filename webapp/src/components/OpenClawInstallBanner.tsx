import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { cn } from "../utils/cn";
import { fetchOpenClawStatus, type OpenClawStatusResponse } from "../services/api";

const DISMISS_KEY = "openclaw-mcp-openclaw-install-dismissed";
const DOCS_URL = "https://openclaw.ai/docs";
const REPO_SECURITY = "https://github.com/sandraschi/openclaw-mcp/blob/main/SECURITY.md";

export default function OpenClawInstallBanner() {
  const [status, setStatus] = useState<OpenClawStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const dismissed = localStorage.getItem(DISMISS_KEY) === "true";
    if (dismissed) {
      setLoading(false);
      return;
    }
    fetchOpenClawStatus()
      .then((res) => {
        if (!cancelled && !res.cli_installed) setVisible(true);
        if (!cancelled) setStatus(res);
      })
      .catch(() => {
        if (!cancelled) setStatus({ cli_installed: false });
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleDismiss = () => {
    localStorage.setItem(DISMISS_KEY, "true");
    setVisible(false);
  };

  if (loading || !visible || !status || status.cli_installed) return null;

  return (
    <div
        role="banner"
        aria-label="OpenClaw not installed"
        className={cn(
          "mb-6 rounded-lg border border-amber-500/50 bg-amber-500/10 px-4 py-3 text-sm text-foreground",
          "animate-fade-in"
        )}
      >
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="font-medium text-foreground">
              OpenClaw CLI was not detected. Install it to use the Gateway and full openclaw-mcp features.
            </p>
            <ul className="mt-2 list-inside list-disc space-y-0.5 text-foreground-secondary">
              <li>
                <strong className="text-foreground">Naked:</strong>{" "}
                <a
                  href={DOCS_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary underline hover:no-underline"
                >
                  openclaw.ai/docs
                </a>{" "}
                (curl / npm install)
              </li>
              <li>
                <strong className="text-foreground">Docker:</strong> Run OpenClaw in a container; see docs for image and compose.
              </li>
              <li>
                <strong className="text-foreground">VM:</strong> Isolate OpenClaw in a VM; see{" "}
                <a
                  href={REPO_SECURITY}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary underline hover:no-underline"
                >
                  SECURITY.md
                </a>{" "}
                for hardening.
              </li>
            </ul>
          </div>
          <button
            type="button"
            onClick={handleDismiss}
            className={cn(
              "shrink-0 rounded-md p-2 text-foreground-secondary transition-colors",
              "hover:bg-muted hover:text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
            )}
            aria-label="Dismiss install banner"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>
  );
}

