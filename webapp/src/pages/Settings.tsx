import { useState, useEffect } from "react";
import { cn } from "../utils/cn";
import {
  fetchOllamaConfig,
  fetchOllamaHealth,
  fetchOllamaTags,
  ollamaPull,
  ollamaDelete,
  type OllamaModelInfo,
} from "../services/api";
import { useLog } from "../context/LogContext";

export default function SettingsPage() {
  const [ollamaOk, setOllamaOk] = useState<boolean | null>(null);
  const [ollamaBase, setOllamaBase] = useState<string>("");
  const [models, setModels] = useState<OllamaModelInfo[]>([]);
  const [pullName, setPullName] = useState("");
  const [pullLoading, setPullLoading] = useState(false);
  const [deletingModel, setDeletingModel] = useState<string | null>(null);
  const { addLog } = useLog();

  useEffect(() => {
    let cancelled = false;
    const timeoutMs = 15000;
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error("Request timed out")), timeoutMs);
    });
    async function load() {
      try {
        const [config, health, tags] = await Promise.all([
          fetchOllamaConfig().catch(() => ({ base: "" })),
          Promise.race([fetchOllamaHealth(), timeoutPromise]),
          Promise.race([fetchOllamaTags(), timeoutPromise]),
        ]);
        if (!cancelled) {
          setOllamaBase(typeof config === "object" && config?.base ? config.base : "");
          setOllamaOk(health.ok);
          setModels(tags.models ?? []);
        }
      } catch {
        if (!cancelled) {
          setOllamaOk(false);
          setModels([]);
        }
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handlePull() {
    const name = pullName.trim();
    if (!name) return;
    setPullLoading(true);
    try {
      await ollamaPull(name);
      const tags = await fetchOllamaTags();
      setModels(tags.models ?? []);
      setPullName("");
    } catch (err) {
      addLog({
        ts: new Date().toISOString(),
        level: "ERROR",
        msg: `Ollama pull failed: ${err instanceof Error ? err.message : err}`,
        source: "client",
      });
    } finally {
      setPullLoading(false);
    }
  }

  async function handleDelete(modelName: string) {
    setDeletingModel(modelName);
    try {
      await ollamaDelete(modelName);
      setModels((prev) => prev.filter((m) => m.name !== modelName));
    } catch (err) {
      addLog({
        ts: new Date().toISOString(),
        level: "ERROR",
        msg: `Ollama delete failed: ${err instanceof Error ? err.message : err}`,
        source: "client",
      });
    } finally {
      setDeletingModel(null);
    }
  }

  return (
    <div className="space-y-10">
      <section>
        <h1 className="font-mono text-3xl font-bold text-foreground">
          Settings
        </h1>
        <p className="mt-2 text-foreground-secondary">
          Ollama models, gateway URL, API keys, and other configuration.
        </p>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-mono text-xl font-semibold text-foreground">
          Ollama
        </h2>
        <p className="mt-1 text-sm text-foreground-secondary">
          Local LLM models. Used by the AI page for quick prompt and chat. Requires Ollama running (e.g. localhost:11434).
        </p>
        <div className="mt-4 flex flex-wrap items-center gap-4">
          <span
            className={cn(
              "inline-flex items-center gap-2 rounded px-3 py-1.5 text-sm font-medium",
              ollamaOk === null
                ? "bg-muted text-foreground-secondary"
                : ollamaOk
                  ? "bg-green-900/40 text-green-300"
                  : "bg-red-900/40 text-red-300"
            )}
          >
            {ollamaOk === null
              ? "Checking..."
              : ollamaOk
                ? "Ollama reachable"
                : "Ollama unreachable"}
          </span>
          {ollamaOk === false && (
            <span className="text-xs text-foreground-tertiary">
              Ensure webapp API (port 5181) and Ollama are running. API uses OLLAMA_BASE: {ollamaBase || "http://localhost:11434"}. If API runs in Docker, set OLLAMA_BASE=http://host.docker.internal:11434.
            </span>
          )}
        </div>
        {ollamaBase && (
          <p className="mt-2 text-xs text-foreground-tertiary">
            API Ollama base: <span className="font-mono">{ollamaBase}</span>
          </p>
        )}

        <div className="mt-4">
          <h3 className="text-sm font-medium text-foreground-secondary">Models</h3>
          <ul className="mt-2 space-y-1 text-sm text-foreground-secondary">
            {models.length === 0 && ollamaOk !== null && (
              <li>No models. Pull one below.</li>
            )}
            {models.map((m) => (
              <li
                key={m.name}
                className="flex items-center justify-between gap-2"
              >
                <span className="font-mono">{m.name}</span>
                <button
                  type="button"
                  onClick={() => handleDelete(m.name)}
                  disabled={deletingModel === m.name}
                  className={cn(
                    "rounded border border-border px-2 py-0.5 text-xs text-red-400 hover:bg-red-900/30 disabled:opacity-50"
                  )}
                >
                  {deletingModel === m.name ? "Deleting..." : "Delete"}
                </button>
              </li>
            ))}
          </ul>
          <div className="mt-3 flex gap-2">
            <input
              type="text"
              value={pullName}
              onChange={(e) => setPullName(e.target.value)}
              placeholder="Model name (e.g. llama3.2)"
              className={cn(
                "flex-1 max-w-xs rounded border border-border bg-background px-3 py-1.5 text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
              disabled={!ollamaOk || pullLoading}
            />
            <button
              type="button"
              onClick={handlePull}
              disabled={!ollamaOk || pullLoading || !pullName.trim()}
              className={cn(
                "rounded border border-primary bg-primary px-3 py-1.5 text-sm text-primary-foreground",
                "hover:bg-primary/90 disabled:opacity-50"
              )}
            >
              {pullLoading ? "Pulling..." : "Pull"}
            </button>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-mono text-xl font-semibold text-foreground">
          Configuration
        </h2>
        <p className="mt-1 text-sm text-foreground-secondary">
          Environment variables (set where you run the webapp API and MCP server).
        </p>
        <ul className="mt-4 space-y-2 text-sm text-foreground-secondary">
          <li>
            <span className="font-mono text-foreground">OPENCLAW_GATEWAY_URL</span> – Gateway URL (default http://127.0.0.1:18789).
          </li>
          <li>
            <span className="font-mono text-foreground">OPENCLAW_GATEWAY_TOKEN</span> – Gateway auth token when enabled.
          </li>
          <li>
            <span className="font-mono text-foreground">OLLAMA_BASE</span> – Ollama API base (default http://localhost:11434).
          </li>
          <li>
            <span className="font-mono text-foreground">MOLTBOOK_API_KEY</span> – For Moltbook registration and API.
          </li>
        </ul>
      </section>
    </div>
  );
}
