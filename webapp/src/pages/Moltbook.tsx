import { useState, useEffect } from "react";
import { MessageSquare, Save, ExternalLink, Send, CheckCircle } from "lucide-react";
import { cn } from "../utils/cn";
import { fetchOpenClawStatus, registerMoltbookAgent } from "../services/api";

const STORAGE_KEY = "clawd-mcp-moltbook-agent-draft";

interface AgentDraft {
  name: string;
  bio: string;
  ideas: string;
  personality: string;
  goals: string;
  updatedAt: string;
}

const defaultDraft: AgentDraft = {
  name: "",
  bio: "",
  ideas: "",
  personality: "",
  goals: "",
  updatedAt: "",
};

export default function Moltbook() {
  const [draft, setDraft] = useState<AgentDraft>(defaultDraft);
  const [saved, setSaved] = useState(false);
  const [openclawInstalled, setOpenclawInstalled] = useState(false);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [registerResult, setRegisterResult] = useState<{ success: boolean; message: string } | null>(null);
  const [registerError, setRegisterError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as AgentDraft;
        setDraft({ ...defaultDraft, ...parsed });
      }
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    fetchOpenClawStatus()
      .then((r) => setOpenclawInstalled(r.cli_installed))
      .catch(() => setOpenclawInstalled(false));
  }, []);

  function handleSave() {
    const next = { ...draft, updatedAt: new Date().toISOString() };
    setDraft(next);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      setSaved(false);
    }
  }

  async function handleRegister() {
    if (!draft.name.trim()) {
      setRegisterError("Agent name is required.");
      return;
    }
    handleSave();
    setRegisterLoading(true);
    setRegisterError(null);
    setRegisterResult(null);
    try {
      const res = await registerMoltbookAgent({
        name: draft.name.trim(),
        bio: draft.bio.trim(),
        personality: draft.personality.trim(),
        goals: draft.goals.trim(),
        ideas: draft.ideas.trim(),
      });
      setRegisterResult({
        success: res.success,
        message: res.message ?? (res.success ? "Registered with Moltbook." : "Registration failed."),
      });
    } catch (err) {
      setRegisterError(err instanceof Error ? err.message : String(err));
    } finally {
      setRegisterLoading(false);
    }
  }

  return (
    <div className="space-y-10">
      <section>
        <h1 className="font-mono text-3xl font-bold text-foreground">
          Moltbook
        </h1>
        <p className="mt-2 text-foreground-secondary">
          Prepare a Moltbook agent: name, bio, personality, goals, and post ideas. Save a draft locally; if OpenClaw is installed, you can send the registration request to Moltbook from here.
        </p>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="flex items-center gap-2 font-mono text-xl font-semibold text-foreground">
          <MessageSquare className="h-5 w-5 text-primary" />
          Prepare agent draft
        </h2>
        <p className="mt-1 text-sm text-foreground-secondary">
          Describe your agent for Moltbook. Saved to browser storage; export or copy into OpenClaw/Moltbook config or skill when ready.
        </p>

        <div className="mt-6 space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">Agent name</span>
            <input
              type="text"
              value={draft.name}
              onChange={(e) => setDraft((p) => ({ ...p, name: e.target.value }))}
              placeholder="e.g. MyMolt"
              className={cn(
                "mt-1 w-full max-w-md rounded border border-border bg-background px-3 py-2 text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">Bio / description</span>
            <textarea
              value={draft.bio}
              onChange={(e) => setDraft((p) => ({ ...p, bio: e.target.value }))}
              placeholder="Short bio for your Moltbook profile"
              rows={2}
              className={cn(
                "mt-1 w-full max-w-2xl rounded border border-border bg-background px-3 py-2 text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">Personality</span>
            <input
              type="text"
              value={draft.personality}
              onChange={(e) => setDraft((p) => ({ ...p, personality: e.target.value }))}
              placeholder="e.g. helpful, concise, technical"
              className={cn(
                "mt-1 w-full max-w-2xl rounded border border-border bg-background px-3 py-2 text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">Goals</span>
            <textarea
              value={draft.goals}
              onChange={(e) => setDraft((p) => ({ ...p, goals: e.target.value }))}
              placeholder="What should this agent do on Moltbook? (e.g. share tips, answer questions)"
              rows={2}
              className={cn(
                "mt-1 w-full max-w-2xl rounded border border-border bg-background px-3 py-2 text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">Post ideas / content themes</span>
            <textarea
              value={draft.ideas}
              onChange={(e) => setDraft((p) => ({ ...p, ideas: e.target.value }))}
              placeholder="Ideas for posts, topics, or content themes. One per line or free-form."
              rows={5}
              className={cn(
                "mt-1 w-full max-w-2xl rounded border border-border bg-background px-3 py-2 text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={handleSave}
            className={cn(
              "flex items-center gap-2 rounded border border-primary bg-primary px-4 py-2 text-sm text-primary-foreground",
              "hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary/50"
            )}
          >
            <Save className="h-4 w-4" />
            {saved ? "Saved" : "Save draft"}
          </button>
          {openclawInstalled && (
            <button
              type="button"
              onClick={handleRegister}
              disabled={registerLoading || !draft.name.trim()}
              className={cn(
                "flex items-center gap-2 rounded border border-primary bg-primary px-4 py-2 text-sm text-primary-foreground",
                "hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
              )}
            >
              <Send className="h-4 w-4" />
              {registerLoading ? "Sending..." : "Register with Moltbook"}
            </button>
          )}
          {draft.updatedAt && (
            <span className="text-xs text-foreground-secondary">
              Last saved: {new Date(draft.updatedAt).toLocaleString()}
            </span>
          )}
        </div>
        {registerError && (
          <p className="mt-3 text-sm text-red-400">{registerError}</p>
        )}
        {registerResult && (
          <div className={cn(
            "mt-3 flex items-center gap-2 rounded border p-3 text-sm",
            registerResult.success
              ? "border-green-500 bg-green-500/10 text-foreground"
              : "border-amber-500 bg-amber-500/10 text-foreground"
          )}>
            {registerResult.success && <CheckCircle className="h-4 w-4 shrink-0 text-green-500" />}
            <span>{registerResult.message}</span>
          </div>
        )}
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-mono text-xl font-semibold text-foreground">
          Preview
        </h2>
        <p className="mt-1 text-sm text-foreground-secondary">
          Summary of your draft for reference.
        </p>
        <div className="mt-4 rounded bg-muted/50 p-4 font-mono text-sm text-foreground-secondary">
          <p><span className="text-foreground">Name:</span> {draft.name || "—"}</p>
          <p><span className="text-foreground">Bio:</span> {draft.bio || "—"}</p>
          <p><span className="text-foreground">Personality:</span> {draft.personality || "—"}</p>
          <p><span className="text-foreground">Goals:</span> {draft.goals || "—"}</p>
          <p><span className="text-foreground">Ideas:</span></p>
          <pre className="mt-1 whitespace-pre-wrap text-foreground-secondary">{draft.ideas || "—"}</pre>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-mono text-xl font-semibold text-foreground">
          Links
        </h2>
        <ul className="mt-4 space-y-2 text-sm text-foreground-secondary">
          <li>
            <a
              href="https://www.moltbook.com"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-primary hover:underline"
            >
              moltbook.com <ExternalLink className="h-3 w-3" />
            </a>
            {" "}
            – Moltbook site
          </li>
          <li>
            <a
              href="https://www.moltbook.com/skill.md"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-primary hover:underline"
            >
              moltbook.com/skill.md <ExternalLink className="h-3 w-3" />
            </a>
            {" "}
            – Moltbook skill for OpenClaw
          </li>
          <li>
            <a
              href="https://www.moltbook.com/heartbeat.md"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-primary hover:underline"
            >
              moltbook.com/heartbeat.md <ExternalLink className="h-3 w-3" />
            </a>
            {" "}
            – Heartbeat pattern for agents
          </li>
        </ul>
      </section>
    </div>
  );
}
