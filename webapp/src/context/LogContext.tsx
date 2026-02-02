import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export interface LogEntry {
  id: string;
  ts: string | null;
  level: string;
  msg: string;
  source?: "client" | "server";
  tool?: string;
  operation?: string;
  error_type?: string;
}

interface LogContextValue {
  entries: LogEntry[];
  addLog: (entry: Omit<LogEntry, "id">) => void;
  clearLogs: () => void;
  logServerUrl: string;
  setLogServerUrl: (url: string) => void;
  fetchLogs: () => Promise<void>;
  fetchError: string | null;
  isFetching: boolean;
}

const LogContext = createContext<LogContextValue | null>(null);

function defaultLogsUrl(): string {
  if (
    typeof import.meta.env?.VITE_LOGS_API_URL === "string" &&
    import.meta.env.VITE_LOGS_API_URL.length > 0
  ) {
    return import.meta.env.VITE_LOGS_API_URL;
  }
  const base =
    typeof import.meta.env?.VITE_API_URL === "string" &&
    import.meta.env.VITE_API_URL.length > 0
      ? import.meta.env.VITE_API_URL.replace(/\/$/, "")
      : "";
  return base ? `${base}/api/logs` : "/api/logs";
}

const defaultLogServerUrl = defaultLogsUrl();

let logId = 0;
function nextId(): string {
  logId += 1;
  return `log-${Date.now()}-${logId}`;
}

export function LogProvider({ children }: { children: ReactNode }) {
  const [clientEntries, setClientEntries] = useState<LogEntry[]>([]);
  const [serverEntries, setServerEntries] = useState<LogEntry[]>([]);
  const [logServerUrl, setLogServerUrlState] = useState(defaultLogServerUrl);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [isFetching, setIsFetching] = useState(false);

  const entries = useMemo(() => {
    const combined = [...clientEntries, ...serverEntries];
    combined.sort((a, b) => {
      const ta = a.ts ? new Date(a.ts).getTime() : 0;
      const tb = b.ts ? new Date(b.ts).getTime() : 0;
      return ta - tb;
    });
    return combined;
  }, [clientEntries, serverEntries]);

  const addLog = useCallback((entry: Omit<LogEntry, "id">) => {
    const newEntry = { ...entry, id: nextId() };
    setClientEntries((prev) => prev.concat([newEntry]).slice(-1000));
  }, []);

  const clearLogs = useCallback(() => {
    setClientEntries([]);
    setServerEntries([]);
    setFetchError(null);
  }, []);

  const fetchLogs = useCallback(async () => {
    setFetchError(null);
    setIsFetching(true);
    try {
      const res = await fetch(`${logServerUrl}?tail=500`);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = (await res.json()) as {
        entries?: Array<{
          ts?: string | null;
          level?: string;
          msg?: string;
          tool?: string;
          operation?: string;
          error_type?: string;
        }>;
      };
      const list: LogEntry[] = (data.entries ?? []).map((e) => ({
        id: nextId(),
        ts: e.ts ?? null,
        level: e.level ?? "INFO",
        msg: e.msg ?? String(e),
        source: "server",
        tool: e.tool,
        operation: e.operation,
        error_type: e.error_type,
      }));
      setServerEntries(list);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setFetchError(message);
      addLog({
        ts: new Date().toISOString(),
        level: "ERROR",
        msg: `Failed to fetch logs: ${message}`,
        source: "client",
      });
    } finally {
      setIsFetching(false);
    }
  }, [logServerUrl, addLog]);

  const setLogServerUrl = useCallback((url: string) => {
    setLogServerUrlState(url);
  }, []);

  const value = useMemo<LogContextValue>(
    () => ({
      entries,
      addLog,
      clearLogs,
      logServerUrl,
      setLogServerUrl,
      fetchLogs,
      fetchError,
      isFetching,
    }),
    [
      entries,
      addLog,
      clearLogs,
      logServerUrl,
      setLogServerUrl,
      fetchLogs,
      fetchError,
      isFetching,
    ]
  );

  return (
    <LogContext.Provider value={value}>{children}</LogContext.Provider>
  );
}

export function useLog(): LogContextValue {
  const ctx = useContext(LogContext);
  if (ctx == null) {
    throw new Error("useLog must be used within LogProvider");
  }
  return ctx;
}
