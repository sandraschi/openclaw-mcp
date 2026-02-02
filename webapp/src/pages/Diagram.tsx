import { useLayoutEffect, useState } from "react";
import { GitBranch } from "lucide-react";
import mermaid from "mermaid";

const DIAGRAM_OPENCLAW = `
flowchart TB
  subgraph Channels["Channels"]
    WA[WhatsApp]
    TG[Telegram]
    DC[Discord]
    SL[Slack]
    WC[WebChat]
  end
  subgraph Gateway["OpenClaw Gateway :18789"]
    HTTP[HTTP API]
    WS[WebSocket]
    HTTP --> Invoke["/tools/invoke"]
    HTTP --> Wake["/hooks/wake"]
    HTTP --> Agent["/hooks/agent"]
  end
  subgraph AgentStack["Agent Stack"]
    Pi[Pi Agent]
    Skills[Skills]
    LLM[LLM]
  end
  Channels --> Gateway
  Gateway --> AgentStack
  Invoke --> Sessions[sessions_list, sessions_history, sessions_send]
  Invoke --> ChannelsTool[channels]
  Invoke --> RoutingTool[routing]
`;

const DIAGRAM_CLAWD_WEBAPP = `
flowchart LR
  subgraph Clients["MCP Clients"]
    Cursor[Cursor]
    Claude[Claude Desktop]
  end
  subgraph clawd["openclaw-mcp"]
    MCP[FastMCP stdio]
    MCP --> Agent[clawd_agent]
    MCP --> Sessions[clawd_sessions]
    MCP --> Channels[clawd_channels]
    MCP --> Routing[clawd_routing]
    MCP --> Skills[clawd_skills]
    MCP --> Gateway[clawd_gateway]
    MCP --> Security[clawd_security]
    MCP --> Moltbook[clawd_moltbook]
  end
  subgraph Webapp["Webapp :5180"]
    React[React + Vite]
    React --> Start[Startpage]
    React --> AI[AI / Ollama]
    React --> Ch[Channels]
    React --> Rt[Routes]
    React --> Int[Integrations]
  end
  subgraph API["Webapp API :5181"]
    FastAPI[FastAPI]
    FastAPI --> Ask["/api/ask"]
    FastAPI --> GW["/api/gateway/status"]
    FastAPI --> ChAPI["/api/channels"]
    FastAPI --> RtAPI["/api/routing"]
    FastAPI --> Ollama["/api/ollama/*"]
  end
  Clients --> MCP
  React --> FastAPI
  Agent --> Gateway
  Sessions --> Gateway
  Channels --> Gateway
  Routing --> Gateway
  Gateway --> Gateway
  ChAPI --> Gateway
  RtAPI --> Gateway
  Ask --> Gateway
  GW --> Gateway
`;

const DIAGRAM_FULL = `
flowchart TB
  subgraph User["User"]
    Browser[Browser :5180]
    IDE[Cursor / Claude]
  end
  subgraph openclaw_mcp["openclaw-mcp"]
    Webapp[Webapp React]
    API[Webapp API :5181]
    MCP[MCP Server stdio]
    Webapp --> API
    IDE --> MCP
  end
  subgraph OpenClaw["OpenClaw"]
    GW[Gateway :18789]
    Ch[Channels]
    Ag[Agent + Skills + LLM]
    GW --> Ch
    GW --> Ag
  end
  subgraph External["External"]
    Moltbook[(Moltbook)]
    Ollama[Ollama :11434]
  end
  API --> GW
  MCP --> GW
  API --> Ollama
  Ag -.-> Moltbook
  MCP --> clawd_moltbook[clawd_moltbook]
  clawd_moltbook --> Moltbook
`;

const diagrams = [
  { id: "diag-openclaw", title: "OpenClaw system", code: DIAGRAM_OPENCLAW },
  { id: "diag-clawd-webapp", title: "openclaw-mcp and webapp", code: DIAGRAM_CLAWD_WEBAPP },
  { id: "diag-full", title: "Full system", code: DIAGRAM_FULL },
];

export default function Diagram() {
  const [svgs, setSvgs] = useState<string[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useLayoutEffect(() => {
    let cancelled = false;
    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      securityLevel: "loose",
      flowchart: { useMaxWidth: true, htmlLabels: true },
    });
    const run = async () => {
      try {
        const results: string[] = [];
        for (let i = 0; i < diagrams.length; i++) {
          const { id, code } = diagrams[i];
          const { svg } = await mermaid.render(`${id}-${Date.now()}-${i}`, code.trim());
          if (!cancelled) results.push(svg);
        }
        if (!cancelled) setSvgs(results);
      } catch (e) {
        if (!cancelled) setErr(e instanceof Error ? e.message : String(e));
      }
    };
    run();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="space-y-10">
      <section>
        <h1 className="font-mono text-3xl font-bold text-foreground">
          Diagrams
        </h1>
        <p className="mt-2 text-foreground-secondary">
          Mermaid diagrams of the OpenClaw system and openclaw-mcp + webapp connections.
        </p>
      </section>

      {err && (
        <p className="rounded border border-red-500/50 bg-red-500/10 px-4 py-2 text-sm text-red-400">
          {err}
        </p>
      )}

      <div className="space-y-10">
        {diagrams.map((d, i) => (
          <section
            key={d.id}
            className="rounded-lg border border-border bg-card p-6"
          >
            <h2 className="flex items-center gap-2 font-mono text-xl font-semibold text-foreground">
              <GitBranch className="h-5 w-5 text-primary" />
              {d.title}
            </h2>
            <div className="mt-4 flex justify-center overflow-auto rounded bg-muted/50 p-4">
              {svgs[i] ? (
                <div
                  className="mermaid-container [&_svg]:max-w-full"
                  dangerouslySetInnerHTML={{ __html: svgs[i] }}
                />
              ) : (
                <p className="text-sm text-foreground-secondary">Rendering...</p>
              )}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}

