import { useCallback, useEffect } from "react";
import { X, RefreshCw, Trash2 } from "lucide-react";
import { cn } from "../../utils/cn";
import { useLog } from "../../context/LogContext";

interface LoggerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

function formatTs(ts: string | null): string {
  if (ts == null) return "";
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString("en-GB", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return ts;
  }
}

function levelColor(level: string): string {
  switch (level.toUpperCase()) {
    case "ERROR":
    case "CRITICAL":
      return "text-red-400";
    case "WARNING":
      return "text-amber-400";
    case "DEBUG":
      return "text-foreground-tertiary";
    default:
      return "text-foreground-secondary";
  }
}

export default function LoggerModal({ isOpen, onClose }: LoggerModalProps) {
  const {
    entries,
    clearLogs,
    fetchLogs,
    fetchError,
    logServerUrl,
    setLogServerUrl,
  } = useLog();

  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [isOpen, onClose]);

  const handleRefresh = useCallback(() => {
    fetchLogs();
  }, [fetchLogs]);

  useEffect(() => {
    if (isOpen && logServerUrl) {
      fetchLogs();
    }
  }, [isOpen, logServerUrl]); // eslint-disable-line react-hooks/exhaustive-deps -- fetch on open only

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="logger-title"
    >
      <div
        className={cn(
          "mx-4 flex max-h-[85vh] w-full max-w-2xl flex-col rounded-lg border border-border",
          "bg-background-secondary shadow-glow animate-fade-in overflow-hidden"
        )}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex shrink-0 items-center justify-between gap-2 border-b border-border px-4 py-3">
          <h2
            id="logger-title"
            className="font-mono text-lg font-semibold text-foreground"
          >
            Logger
          </h2>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={logServerUrl}
              onChange={(e) => setLogServerUrl(e.target.value)}
              placeholder="Log server URL"
              className={cn(
                "w-48 rounded border border-border bg-background px-2 py-1.5 font-mono text-xs text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
              title="Log server URL (e.g. http://127.0.0.1:8765/api/logs)"
            />
            <button
              type="button"
              onClick={handleRefresh}
              className={cn(
                "rounded-md p-2 text-foreground-secondary transition-colors",
                "hover:bg-muted hover:text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
              )}
              aria-label="Refresh logs"
              title="Fetch logs from server"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={clearLogs}
              className={cn(
                "rounded-md p-2 text-foreground-secondary transition-colors",
                "hover:bg-muted hover:text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
              )}
              aria-label="Clear logs"
              title="Clear log buffer"
            >
              <Trash2 className="h-4 w-4" />
            </button>
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
        </div>
        {fetchError != null && (
          <div className="shrink-0 border-b border-border bg-muted/50 px-4 py-2 text-xs text-amber-400">
            Server error: {fetchError}. Ensure the webapp API (port 5181) is running, or set a custom log URL (e.g. http://127.0.0.1:8765/api/logs after running: python -m openclaw_mcp.serve_logs).
          </div>
        )}
        <div className="flex-1 overflow-y-auto bg-background p-4 font-mono text-xs">
          {entries.length === 0 ? (
            <p className="text-foreground-tertiary">
              No log entries. Logs are read from the API (same backend as the
              dashboard). Run the MCP server to generate entries, then click
              Refresh.
            </p>
          ) : (
            <ul className="space-y-1">
              {entries.map((e) => (
                <li
                  key={e.id}
                  className={cn(
                    "flex flex-wrap gap-x-2 gap-y-0.5 border-b border-border/50 py-1",
                    levelColor(e.level)
                  )}
                >
                  <span className="shrink-0 text-foreground-tertiary">
                    {formatTs(e.ts)}
                  </span>
                  <span
                    className={cn(
                      "shrink-0 font-semibold",
                      levelColor(e.level)
                    )}
                  >
                    [{e.level}]
                  </span>
                  {e.tool != null && (
                    <span className="shrink-0 text-primary">{e.tool}</span>
                  )}
                  {e.operation != null && (
                    <span className="shrink-0 text-foreground-tertiary">
                      {e.operation}
                    </span>
                  )}
                  <span className="min-w-0 flex-1 break-all">{e.msg}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

