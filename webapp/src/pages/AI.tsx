import { useState, useEffect, useRef } from "react";
import { Send, Loader2 } from "lucide-react";
import { cn } from "../utils/cn";
import {
  fetchOllamaHealth,
  fetchOllamaTags,
  ollamaGenerate,
  ollamaChat,
  type OllamaModelInfo,
  type ChatMessagePayload,
} from "../services/api";
import { useLog } from "../context/LogContext";

const SHORTCUTS = [
  { label: "Explain last log", prompt: "Summarize the last 20 lines of the openclaw-mcp log file and explain any errors or warnings." },
  { label: "Summarize security findings", prompt: "List and briefly explain the main security recommendations for running OpenClaw (gateway binding, skills, sandbox)." },
  { label: "OpenClaw vs Moltbook", prompt: "In 3 short bullets: what is OpenClaw, what is Moltbook, and how do they relate?" },
];

const PERSONALITIES: { id: string; label: string; system: string | null }[] = [
  { id: "normal", label: "Normal (OpenClaw/Moltbook helper)", system: null },
  { id: "concise", label: "Concise (short answers)", system: "You are a helpful assistant. Answer in one to three short sentences. No fluff." },
  { id: "pirate", label: "Pirate captain", system: "You are a pirate captain. Reply in character with nautical slang, 'arr', and maritime humor. Stay helpful." },
  { id: "mork", label: "Mork from Ork", system: "You are Mork from Ork (Mork & Mindy). Reply in character: say 'Nanu nanu', speak in Orkan style, be whimsical and kind. Stay helpful." },
  { id: "friar", label: "Medieval friar (Latin)", system: "You are a medieval friar. Reply in character, mostly in Latin (with brief English when needed). Be scholarly and gentle. Stay helpful." },
  { id: "japanese_cop", label: "Japanese cop (Japanese)", system: "You are a Japanese police officer. Reply in character, speaking primarily in Japanese (use romaji or short English glosses). Be formal and helpful." },
  { id: "shakespeare", label: "Shakespeare", system: "You are William Shakespeare. Reply in character, in early modern English verse or prose. Be witty and helpful." },
  { id: "robot", label: "Friendly robot", system: "You are a friendly robot. Reply in character: beep, use short mechanical phrasing, stay kind and helpful." },
];

export default function AI() {
  const [ollamaOk, setOllamaOk] = useState<boolean | null>(null);
  const [models, setModels] = useState<OllamaModelInfo[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [selectedPersonality, setSelectedPersonality] = useState<string>("normal");
  const [quickPrompt, setQuickPrompt] = useState("");
  const [quickResponse, setQuickResponse] = useState<string | null>(null);
  const [quickError, setQuickError] = useState<string | null>(null);
  const [quickLoading, setQuickLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessagePayload[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const { addLog } = useLog();

  useEffect(() => {
    let cancelled = false;
    const timeoutMs = 15000;
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error("Request timed out")), timeoutMs);
    });
    async function load() {
      try {
        const [health, tags] = await Promise.all([
          Promise.race([fetchOllamaHealth(), timeoutPromise]),
          Promise.race([fetchOllamaTags(), timeoutPromise]),
        ]);
        if (!cancelled) {
          setOllamaOk(health.ok);
          setModels(tags.models ?? []);
          if (tags.models?.length && !selectedModel) {
            setSelectedModel(tags.models[0].name ?? "");
          }
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

  useEffect(() => {
    if (models.length && !selectedModel) setSelectedModel(models[0].name ?? "");
  }, [models, selectedModel]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  async function handleQuickPrompt() {
    const prompt = quickPrompt.trim();
    if (!prompt || !selectedModel) return;
    setQuickLoading(true);
    setQuickError(null);
    setQuickResponse(null);
    try {
      const personality = PERSONALITIES.find((p) => p.id === selectedPersonality);
      const system = personality?.system ?? undefined;
      const res = await ollamaGenerate({ model: selectedModel, prompt, system });
      setQuickResponse(res.response ?? "");
    } catch (err) {
      const text = err instanceof Error ? err.message : String(err);
      setQuickError(text);
      addLog({
        ts: new Date().toISOString(),
        level: "ERROR",
        msg: `Ollama generate failed: ${text}`,
        source: "client",
      });
    } finally {
      setQuickLoading(false);
    }
  }

  async function handleChatSend() {
    const text = chatInput.trim();
    if (!text || !selectedModel) return;
    const userMsg: ChatMessagePayload = { role: "user", content: text };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setChatLoading(true);
    try {
      const messages: ChatMessagePayload[] = [...chatMessages, userMsg];
      const personality = PERSONALITIES.find((p) => p.id === selectedPersonality);
      const system = personality?.system ?? undefined;
      const res = await ollamaChat({ model: selectedModel, messages, system });
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.response ?? "" },
      ]);
    } catch (err) {
      const errorText = err instanceof Error ? err.message : String(err);
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${errorText}` },
      ]);
      addLog({
        ts: new Date().toISOString(),
        level: "ERROR",
        msg: `Ollama chat failed: ${errorText}`,
        source: "client",
      });
    } finally {
      setChatLoading(false);
    }
  }

  return (
    <div className="space-y-10">
      <section>
        <h1 className="font-mono text-3xl font-bold text-foreground">AI</h1>
        <p className="mt-2 text-foreground-secondary">
          Local LLM via Ollama. Quick prompt, shortcuts, and chat. Pick a model in Settings if none appear.
        </p>
        <div className="mt-4 flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-foreground-secondary">
            Model:
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className={cn(
                "rounded border border-border bg-background px-2 py-1 text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            >
              {models.map((m) => (
                <option key={m.name} value={m.name}>
                  {m.name}
                </option>
              ))}
              {!models.length && <option value="">No models</option>}
            </select>
          </label>
          <label className="flex items-center gap-2 text-sm text-foreground-secondary">
            Personality:
            <select
              value={selectedPersonality}
              onChange={(e) => setSelectedPersonality(e.target.value)}
              className={cn(
                "rounded border border-border bg-background px-2 py-1 text-foreground min-w-[200px]",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            >
              {PERSONALITIES.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
            </select>
          </label>
          {ollamaOk === false && (
            <span className="text-xs text-foreground-tertiary">
              Ollama unreachable. Check Settings (Ollama) and ensure API (5181) and Ollama (11434) are running.
            </span>
          )}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-mono text-xl font-semibold text-foreground">
          Quick prompt
        </h2>
        <p className="mt-1 text-sm text-foreground-secondary">
          One-off generate with selected model. No chat history.
        </p>
        <div className="mt-4 flex gap-2">
          <textarea
            value={quickPrompt}
            onChange={(e) => setQuickPrompt(e.target.value)}
            placeholder="Ask something..."
            rows={2}
            className={cn(
              "flex-1 rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
              "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            )}
            disabled={quickLoading || !ollamaOk}
          />
          <button
            type="button"
            onClick={handleQuickPrompt}
            disabled={quickLoading || !ollamaOk || !selectedModel || !quickPrompt.trim()}
            className={cn(
              "rounded border border-primary bg-primary px-4 py-2 text-primary-foreground",
              "hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
            )}
          >
            {quickLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>
        {quickError && <p className="mt-2 text-sm text-red-400">{quickError}</p>}
        {quickResponse && (
          <div className="mt-3 rounded bg-muted p-3 text-sm text-foreground-secondary whitespace-pre-wrap">
            {quickResponse}
          </div>
        )}

        <div className="mt-4">
          <h3 className="text-sm font-medium text-foreground-secondary">Shortcuts</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {SHORTCUTS.map((s) => (
              <button
                key={s.label}
                type="button"
                onClick={() => setQuickPrompt(s.prompt)}
                className={cn(
                  "rounded border border-border bg-muted px-3 py-1.5 text-xs text-foreground-secondary",
                  "hover:bg-muted/80 hover:text-foreground"
                )}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-mono text-xl font-semibold text-foreground">
          Chat
        </h2>
        <p className="mt-1 text-sm text-foreground-secondary">
          Conversation with system preprompt (OpenClaw/Moltbook context). Uses selected model.
        </p>
        <div className="mt-4 flex h-64 flex-col overflow-hidden rounded border border-border bg-background">
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {chatMessages.length === 0 && (
              <p className="text-sm text-foreground-secondary">No messages yet. Send one below.</p>
            )}
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  "rounded px-3 py-2 text-sm",
                  msg.role === "user"
                    ? "ml-8 bg-primary/20 text-foreground"
                    : "mr-8 bg-muted text-foreground-secondary"
                )}
              >
                <span className="font-medium text-foreground-secondary">{msg.role}: </span>
                <span className="whitespace-pre-wrap">{msg.content}</span>
              </div>
            ))}
            {chatLoading && (
              <div className="flex items-center gap-2 text-sm text-foreground-secondary">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Thinking...</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          <div className="flex gap-2 border-t border-border p-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleChatSend()}
              placeholder="Type a message..."
              className={cn(
                "flex-1 rounded border border-border bg-background px-3 py-2 text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
              disabled={chatLoading || !ollamaOk}
            />
            <button
              type="button"
              onClick={handleChatSend}
              disabled={chatLoading || !ollamaOk || !selectedModel || !chatInput.trim()}
              className={cn(
                "rounded border border-primary bg-primary px-4 py-2 text-primary-foreground",
                "hover:bg-primary/90 disabled:opacity-50"
              )}
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

