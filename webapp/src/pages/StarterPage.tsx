import { useState, useEffect } from "react";
import { Globe, FileCode, ExternalLink, CheckCircle, Settings } from "lucide-react";
import { cn } from "../utils/cn";
import {
  generateLandingPage,
  type LandingPageRequest,
  fetchMcpConfigClients,
  insertMcpConfig,
  type McpConfigClient,
  type McpConfigInsertResponse,
} from "../services/api";

const DEPLOY_HINTS = [
  {
    name: "GitHub Pages",
    url: "https://pages.github.com",
    hint: "Push the www folder to a repo, then Settings > Pages > Deploy from branch.",
  },
  {
    name: "Netlify",
    url: "https://netlify.com",
    hint: "Drag and drop the www folder or connect Git and set Publish directory to www.",
  },
  {
    name: "Vercel",
    url: "https://vercel.com",
    hint: "Import Git repo; set Root/Output directory to the folder containing www.",
  },
  {
    name: "Cloudflare Pages",
    url: "https://pages.cloudflare.com",
    hint: "Direct Upload the www folder or connect Git; set build output to www.",
  },
];

const DEFAULT_FEATURES = [
  "Blazing Fast: Engineered for maximum velocity and minimum drag.",
  "Secure by Design: Fort Knox level security for your data.",
  "Open Source: Transparency is key. Code is law.",
];

export default function StarterPage() {
  const [projectName, setProjectName] = useState("India Claw");
  const [heroTitle, setHeroTitle] = useState("India Claw");
  const [heroSubtitle, setHeroSubtitle] = useState(
    "Your AI presence on the web. Built with OpenClaw and openclaw-mcp."
  );
  const [featuresText, setFeaturesText] = useState(DEFAULT_FEATURES.join("\n"));
  const [githubUrl, setGithubUrl] = useState("https://github.com");
  const [authorName, setAuthorName] = useState("Developer");
  const [authorBio, setAuthorBio] = useState(
    "I build things. Powered by OpenClaw, Moltbook, and openclaw-mcp."
  );
  const [donateLink, setDonateLink] = useState("#");
  const [heroImageKeyword, setHeroImageKeyword] = useState("blue lobster");
  const [includePictures, setIncludePictures] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ path: string; message: string; index_url?: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [mcpClients, setMcpClients] = useState<McpConfigClient[]>([]);
  const [mcpSelected, setMcpSelected] = useState<Set<string>>(new Set());
  const [mcpInsertLoading, setMcpInsertLoading] = useState(false);
  const [mcpInsertResult, setMcpInsertResult] = useState<McpConfigInsertResponse | null>(null);
  const [mcpInsertError, setMcpInsertError] = useState<string | null>(null);

  const [gatewayUrl, setGatewayUrl] = useState("http://127.0.0.1:18789");
  const [gatewayToken, setGatewayToken] = useState("");
  const [openclawSnippet, setOpenclawSnippet] = useState<{ env: string; hint: string } | null>(null);

  useEffect(() => {
    fetchMcpConfigClients()
      .then((r) => setMcpClients(r.clients || []))
      .catch(() => setMcpClients([]));
  }, []);

  function handleMcpToggle(id: string) {
    setMcpSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function handleOpenClawSnippet() {
    const url = gatewayUrl.trim() || "http://127.0.0.1:18789";
    const token = gatewayToken.trim();
    const envLines = [
      "# OpenClaw Gateway (openclaw-mcp, webapp)",
      `OPENCLAW_GATEWAY_URL=${url}`,
    ];
    if (token) {
      envLines.push(`OPENCLAW_GATEWAY_TOKEN=${token}`);
    } else {
      envLines.push("# OPENCLAW_GATEWAY_TOKEN=  # set if Gateway auth is enabled");
    }
    envLines.push("# MOLTBOOK_API_KEY=  # optional");
    const env = envLines.join("\n");
    const hint = "Routing: OpenClaw stores channel-to-agent rules in ~/.openclaw/openclaw.json. Use the webapp Routes page or MCP tool clawd_routing to view/update. See INSTALL.md for config locations.";
    setOpenclawSnippet({ env, hint });
  }

  async function handleMcpInsert() {
    if (mcpSelected.size === 0) {
      setMcpInsertError("Select at least one client.");
      return;
    }
    setMcpInsertLoading(true);
    setMcpInsertError(null);
    setMcpInsertResult(null);
    try {
      const res = await insertMcpConfig({ clients: Array.from(mcpSelected) });
      setMcpInsertResult(res);
    } catch (err) {
      setMcpInsertError(err instanceof Error ? err.message : String(err));
    } finally {
      setMcpInsertLoading(false);
    }
  }

  async function handleGenerate() {
    const name = projectName.trim();
    if (!name) {
      setError("Project name is required.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    const features = featuresText
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);
    const body: LandingPageRequest = {
      project_name: name,
      hero_title: heroTitle.trim() || "The Next Big Thing",
      hero_subtitle: heroSubtitle.trim(),
      features: features.length > 0 ? features : undefined,
      github_url: githubUrl.trim(),
      author_name: authorName.trim(),
      author_bio: authorBio.trim(),
      donate_link: donateLink.trim(),
      hero_image_keyword: heroImageKeyword.trim() || "blue lobster",
      include_pictures: includePictures,
    };
    try {
      const res = await generateLandingPage(body);
      if (res.success && res.path && res.message) {
        setResult({ path: res.path, message: res.message, index_url: res.index_url });
      } else {
        setError(res.message ?? "Generation failed.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-10">
      <section>
        <h1 className="flex items-center gap-2 font-mono text-3xl font-bold text-foreground">
          <Globe className="h-8 w-5 text-primary" />
          Generate
        </h1>
        <p className="mt-2 text-foreground-secondary">
          Landing pages, and more. Start with a static hero site (HTML/CSS/JS + DEPLOY.md); more generators may be added here.
        </p>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="flex items-center gap-2 font-mono text-xl font-semibold text-foreground">
          <FileCode className="h-5 w-5 text-primary" />
          Options
        </h2>
        <p className="mt-1 text-sm text-foreground-secondary">
          Project name and hero title (e.g. India Claw). Features: one per line, optional "Title: Description". Output: ./generated/&lt;project_slug&gt;/www (override with LANDING_PAGE_OUTPUT_DIR).
        </p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <label className="block sm:col-span-2">
            <span className="text-sm font-medium text-foreground-secondary">Project name</span>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="e.g. India Claw"
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">Hero title</span>
            <input
              type="text"
              value={heroTitle}
              onChange={(e) => setHeroTitle(e.target.value)}
              placeholder="e.g. India Claw"
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">Hero image keyword</span>
            <input
              type="text"
              value={heroImageKeyword}
              onChange={(e) => setHeroImageKeyword(e.target.value)}
              placeholder="e.g. blue lobster"
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block sm:col-span-2 flex items-center gap-2">
            <input
              type="checkbox"
              checked={includePictures}
              onChange={(e) => setIncludePictures(e.target.checked)}
              className="rounded border-border text-primary focus:ring-primary"
            />
            <span className="text-sm font-medium text-foreground-secondary">Include pictures</span>
          </label>
          <label className="block sm:col-span-2">
            <span className="text-sm font-medium text-foreground-secondary">Hero subtitle</span>
            <input
              type="text"
              value={heroSubtitle}
              onChange={(e) => setHeroSubtitle(e.target.value)}
              placeholder="Short tagline"
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block sm:col-span-2">
            <span className="text-sm font-medium text-foreground-secondary">Features (one per line, optional "Title: Description")</span>
            <textarea
              value={featuresText}
              onChange={(e) => setFeaturesText(e.target.value)}
              rows={4}
              placeholder="Blazing Fast: Engineered for speed."
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">Author name</span>
            <input
              type="text"
              value={authorName}
              onChange={(e) => setAuthorName(e.target.value)}
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">GitHub URL</span>
            <input
              type="url"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder="https://github.com/..."
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block sm:col-span-2">
            <span className="text-sm font-medium text-foreground-secondary">Author bio</span>
            <textarea
              value={authorBio}
              onChange={(e) => setAuthorBio(e.target.value)}
              rows={2}
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block sm:col-span-2">
            <span className="text-sm font-medium text-foreground-secondary">Donate link (Patreon, Ko-fi, etc.)</span>
            <input
              type="url"
              value={donateLink}
              onChange={(e) => setDonateLink(e.target.value)}
              placeholder="#"
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
        </div>

        <div className="mt-6">
          <button
            type="button"
            onClick={handleGenerate}
            disabled={loading}
            className={cn(
              "rounded border border-primary bg-primary px-4 py-2 text-primary-foreground",
              "hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
            )}
          >
            {loading ? "Generating..." : "Generate landing page"}
          </button>
        </div>

        {error && (
          <p className="mt-4 text-sm text-red-400">{error}</p>
        )}
        {result && (
          <div className="mt-4 rounded-lg border-2 border-green-500 bg-green-500/10 p-6">
            <div className="flex items-start gap-3">
              <CheckCircle className="h-6 w-6 shrink-0 text-green-500 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold text-foreground text-lg">{result.message}</p>
                {result.index_url && (
                  <div className="mt-4 flex flex-wrap gap-3">
                    <a
                      href={result.index_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={cn(
                        "inline-flex items-center gap-2 rounded border-2 border-green-500 bg-green-500 px-4 py-2 text-sm font-medium text-white",
                        "hover:bg-green-600 hover:border-green-600 focus:outline-none focus:ring-2 focus:ring-green-500/50"
                      )}
                    >
                      <ExternalLink className="h-4 w-4" />
                      Open landing page
                    </a>
                  </div>
                )}
                <p className="mt-3 text-sm text-foreground-secondary">
                  See <span className="font-mono">DEPLOY.md</span> in the project folder for deployment instructions.
                </p>
              </div>
            </div>
          </div>
        )}
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="flex items-center gap-2 font-mono text-xl font-semibold text-foreground">
          <FileCode className="h-5 w-5 text-primary" />
          OpenClaw env / config snippet
        </h2>
        <p className="mt-2 text-sm text-foreground-secondary">
          For docs or onboarding. Generates a .env.example-style block and a short routing hint. Paste into your project or README.
        </p>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">Gateway URL</span>
            <input
              type="url"
              value={gatewayUrl}
              onChange={(e) => setGatewayUrl(e.target.value)}
              placeholder="http://127.0.0.1:18789"
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-foreground-secondary">Token (optional)</span>
            <input
              type="text"
              value={gatewayToken}
              onChange={(e) => setGatewayToken(e.target.value)}
              placeholder="leave empty if Gateway has no auth"
              className={cn(
                "mt-1 w-full rounded border border-border bg-background px-4 py-2 font-mono text-sm text-foreground",
                "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              )}
            />
          </label>
        </div>
        <div className="mt-4">
          <button
            type="button"
            onClick={handleOpenClawSnippet}
            className={cn(
              "rounded border border-primary bg-primary px-4 py-2 text-primary-foreground",
              "hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary/50"
            )}
          >
            Generate snippet
          </button>
        </div>
        {openclawSnippet && (
          <div className="mt-4 space-y-3">
            <div>
              <span className="text-sm font-medium text-foreground-secondary">.env.example</span>
              <pre className="mt-1 rounded border border-border bg-muted p-3 font-mono text-xs text-foreground overflow-x-auto whitespace-pre-wrap break-all">
                {openclawSnippet.env}
              </pre>
            </div>
            <div>
              <span className="text-sm font-medium text-foreground-secondary">Routing / config hint</span>
              <p className="mt-1 text-sm text-foreground-secondary">{openclawSnippet.hint}</p>
            </div>
          </div>
        )}
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="flex items-center gap-2 font-mono text-xl font-semibold text-foreground">
          <Settings className="h-5 w-5 text-primary" />
          MCP config snippet
        </h2>
        <p className="mt-2 rounded border border-amber-500/50 bg-amber-500/10 px-3 py-2 text-sm text-foreground-secondary">
          Use with caution. This will modify your MCP client config file(s) and create timestamped backups. If openclaw-mcp is already present, it will not be added again (no multi-insert).
        </p>
        <p className="mt-2 text-sm text-foreground-secondary">
          Select one or more clients; the openclaw-mcp snippet (PYTHONPATH to this repo) will be inserted into their config. Restart the client after inserting.
        </p>
        <div className="mt-4 flex flex-wrap gap-4">
          {mcpClients.map((c) => (
            <label key={c.id} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={mcpSelected.has(c.id)}
                onChange={() => handleMcpToggle(c.id)}
                className="rounded border-border text-primary focus:ring-primary"
              />
              <span className="text-sm text-foreground-secondary">{c.label}</span>
              {c.path && (
                <span className="text-xs text-foreground-tertiary" title={c.path}>
                  {c.exists ? "(exists)" : "(path only)"}
                </span>
              )}
            </label>
          ))}
        </div>
        <div className="mt-4">
          <button
            type="button"
            onClick={handleMcpInsert}
            disabled={mcpInsertLoading || mcpSelected.size === 0}
            className={cn(
              "rounded border border-primary bg-primary px-4 py-2 text-primary-foreground",
              "hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
            )}
          >
            {mcpInsertLoading ? "Inserting..." : "Insert into selected configs"}
          </button>
        </div>
        {mcpInsertError && (
          <p className="mt-4 text-sm text-red-400">{mcpInsertError}</p>
        )}
        {mcpInsertResult && (
          <div className="mt-4 rounded-lg border-2 border-green-500 bg-green-500/10 p-4">
            <div className="flex items-start gap-2">
              <CheckCircle className="h-5 w-5 shrink-0 text-green-500 mt-0.5" />
              <div className="text-sm text-foreground-secondary">
                <p className="font-medium text-foreground">Done.</p>
                {mcpInsertResult.updated.length > 0 && (
                  <p className="mt-1">Updated: {mcpInsertResult.updated.join(", ")}. Backups created where applicable.</p>
                )}
                {mcpInsertResult.skipped.length > 0 && (
                  <p className="mt-1">Skipped (already present): {mcpInsertResult.skipped.join(", ")}.</p>
                )}
                {Object.keys(mcpInsertResult.errors).length > 0 && (
                  <p className="mt-1 text-amber-600">Errors: {Object.entries(mcpInsertResult.errors).map(([k, v]) => `${k}: ${v}`).join("; ")}.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="font-mono text-xl font-semibold text-foreground">
          How to get your page online
        </h2>
        <p className="mt-1 text-sm text-foreground-secondary">
          After generating, upload the contents of the www folder to any static host. No build step. DEPLOY.md in the project folder has the same hints.
        </p>
        <ul className="mt-4 space-y-4">
          {DEPLOY_HINTS.map((d) => (
            <li key={d.name} className="flex flex-col gap-1">
              <a
                href={d.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 font-medium text-primary hover:underline"
              >
                {d.name}
                <ExternalLink className="h-4 w-4" />
              </a>
              <span className="text-sm text-foreground-secondary">{d.hint}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

