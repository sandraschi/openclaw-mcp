/**
 * Webapp API client. Uses same-origin /api when Vite proxy is active (dev) or VITE_API_URL in production.
 */

const API_BASE =
  typeof import.meta.env?.VITE_API_URL === "string" &&
  import.meta.env.VITE_API_URL.length > 0
    ? import.meta.env.VITE_API_URL.replace(/\/$/, "")
    : "";

function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return API_BASE ? `${API_BASE}${p}` : p;
}

export interface AskResponse {
  success: boolean;
  message: string;
  data?: Record<string, unknown>;
  error?: string;
}

export async function askOpenClaw(message: string): Promise<AskResponse> {
  const res = await fetch(apiUrl("/api/ask"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Ask failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<AskResponse>;
}

export interface GatewayStatusResponse {
  success: boolean;
  message: string;
  data?: unknown;
  error?: string;
}

export async function fetchGatewayStatus(): Promise<GatewayStatusResponse> {
  const res = await fetch(apiUrl("/api/gateway/status"));
  if (!res.ok) throw new Error(`Gateway status failed: ${res.status}`);
  return res.json() as Promise<GatewayStatusResponse>;
}

export interface OpenClawStatusResponse {
  cli_installed: boolean;
  version?: string | null;
}

export async function fetchOpenClawStatus(): Promise<OpenClawStatusResponse> {
  const res = await fetch(apiUrl("/api/openclaw/status"));
  if (!res.ok) throw new Error(`OpenClaw status failed: ${res.status}`);
  return res.json() as Promise<OpenClawStatusResponse>;
}

export interface MoltbookRegisterRequest {
  name: string;
  bio?: string;
  personality?: string;
  goals?: string;
  ideas?: string;
}

export interface MoltbookRegisterResponse {
  success: boolean;
  message?: string;
  data?: Record<string, unknown>;
  error?: string;
}

export async function registerMoltbookAgent(
  body: MoltbookRegisterRequest
): Promise<MoltbookRegisterResponse> {
  const res = await fetch(apiUrl("/api/moltbook/register"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Moltbook register failed: ${res.status}`);
  }
  return res.json() as Promise<MoltbookRegisterResponse>;
}

export interface SkillsResponse {
  success: boolean;
  skills: string[];
  path: string;
}

export async function fetchSkills(): Promise<SkillsResponse> {
  const res = await fetch(apiUrl("/api/skills"));
  if (!res.ok) throw new Error(`Skills failed: ${res.status}`);
  return res.json() as Promise<SkillsResponse>;
}

export interface ClawNewsItem {
  title: string;
  source: string;
  url: string;
  date: string;
}

export interface ClawNewsResponse {
  success: boolean;
  items: ClawNewsItem[];
}

export async function fetchClawNews(): Promise<ClawNewsResponse> {
  const res = await fetch(apiUrl("/api/clawnews"));
  if (!res.ok) throw new Error(`Clawnews failed: ${res.status}`);
  return res.json() as Promise<ClawNewsResponse>;
}

// --- Ollama ---

export interface OllamaHealthResponse {
  ok: boolean;
}

export async function fetchOllamaHealth(): Promise<OllamaHealthResponse> {
  const res = await fetch(apiUrl("/api/ollama/health"));
  if (!res.ok) throw new Error(`Ollama health failed: ${res.status}`);
  return res.json() as Promise<OllamaHealthResponse>;
}

export interface OllamaModelInfo {
  name: string;
  size?: number;
  [key: string]: unknown;
}

export interface OllamaTagsResponse {
  success: boolean;
  models: OllamaModelInfo[];
}

export async function fetchOllamaTags(): Promise<OllamaTagsResponse> {
  const res = await fetch(apiUrl("/api/ollama/tags"));
  if (!res.ok) throw new Error(`Ollama tags failed: ${res.status}`);
  return res.json() as Promise<OllamaTagsResponse>;
}

export interface OllamaGenerateRequest {
  model: string;
  prompt: string;
  system?: string;
}

export interface OllamaGenerateResponse {
  success: boolean;
  response: string;
  raw?: Record<string, unknown>;
}

export async function ollamaGenerate(
  body: OllamaGenerateRequest
): Promise<OllamaGenerateResponse> {
  const res = await fetch(apiUrl("/api/ollama/generate"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Ollama generate failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<OllamaGenerateResponse>;
}

export interface ChatMessagePayload {
  role: string;
  content: string;
}

export interface OllamaChatRequest {
  model: string;
  messages: ChatMessagePayload[];
  system?: string;
}

export interface OllamaChatResponse {
  success: boolean;
  message?: { role: string; content: string };
  response: string;
  raw?: Record<string, unknown>;
}

export async function ollamaChat(
  body: OllamaChatRequest
): Promise<OllamaChatResponse> {
  const res = await fetch(apiUrl("/api/ollama/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Ollama chat failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<OllamaChatResponse>;
}

export async function ollamaPull(name: string): Promise<{ success: boolean }> {
  const res = await fetch(apiUrl("/api/ollama/pull"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Ollama pull failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<{ success: boolean }>;
}

export async function ollamaDelete(name: string): Promise<{ success: boolean }> {
  const res = await fetch(apiUrl("/api/ollama/delete"), {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Ollama delete failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<{ success: boolean }>;
}

// --- Channels ---

export interface ChannelsRequest {
  operation: string;
  channel?: string;
  to?: string;
  message?: string;
  limit?: number;
  session_key?: string;
  args?: Record<string, unknown>;
}

export interface ChannelsResponse {
  success: boolean;
  message: string;
  data?: unknown;
  error?: string;
}

export async function channelsApi(
  body: ChannelsRequest
): Promise<ChannelsResponse> {
  const res = await fetch(apiUrl("/api/channels"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Channels failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<ChannelsResponse>;
}

// --- Routing ---

export interface RoutingRequest {
  operation: string;
  channel?: string;
  agent?: string;
  peer?: string;
  body?: string;
  session_key?: string;
  args?: Record<string, unknown>;
}

export interface RoutingResponse {
  success: boolean;
  message: string;
  data?: unknown;
  error?: string;
}

export async function routingApi(
  body: RoutingRequest
): Promise<RoutingResponse> {
  const res = await fetch(apiUrl("/api/routing"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Routing failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<RoutingResponse>;
}

// --- Landing page (starter web presence) ---

export interface LandingPageRequest {
  project_name: string;
  hero_title?: string;
  hero_subtitle?: string;
  features?: string[];
  github_url?: string;
  author_name?: string;
  author_bio?: string;
  donate_link?: string;
  hero_image_keyword?: string;
  include_pictures?: boolean;
}

export interface LandingPageResponse {
  success: boolean;
  path?: string;
  index_url?: string;
  message?: string;
}

export async function generateLandingPage(
  body: LandingPageRequest
): Promise<LandingPageResponse> {
  const res = await fetch(apiUrl("/api/landing-page"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Landing page failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<LandingPageResponse>;
}

// --- MCP config insert ---

export interface McpConfigClient {
  id: string;
  label: string;
  path: string | null;
  exists: boolean;
}

export interface McpConfigClientsResponse {
  success: boolean;
  clients: McpConfigClient[];
}

export async function fetchMcpConfigClients(): Promise<McpConfigClientsResponse> {
  const res = await fetch(apiUrl("/api/mcp-config/clients"));
  if (!res.ok) throw new Error(`MCP config clients failed: ${res.status}`);
  return res.json() as Promise<McpConfigClientsResponse>;
}

export interface McpConfigInsertRequest {
  clients: string[];
}

export interface McpConfigInsertResponse {
  success: boolean;
  updated: string[];
  skipped: string[];
  backups: Record<string, string>;
  errors: Record<string, string>;
  message: string;
}

export async function insertMcpConfig(
  body: McpConfigInsertRequest
): Promise<McpConfigInsertResponse> {
  const res = await fetch(apiUrl("/api/mcp-config/insert"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`MCP config insert failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<McpConfigInsertResponse>;
}
