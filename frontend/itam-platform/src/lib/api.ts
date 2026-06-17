import type { AiChatConversation, AiChatConversationCreate, AiChatConversationDetail, AiChatMessageCreate, AiChatProviderHealth, Asset, AuditLog, ImportConflict, ImportJob, ImportPreview, ImportStagingAsset, ImportValidationError, MacroAutocompleteHint, MacroGeneration, MacroRenderResponse, MacroTemplate, Movement, Page, SearchResponse, SuggestedMovementMacro, TokenResponse, User } from "./types";

const API_BASE = (import.meta.env.VITE_API_URL || "/api/v1").replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string | null;

  constructor(message: string, status: number, detail: string | null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function normalizeErrorDetail(value: unknown): string | null {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value === "string") {
    return value;
  }
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

export function mapAiChatError(error: unknown): {
  title: string;
  message: string;
  severity: "warning" | "danger";
  technical?: string;
} {
  if (!(error instanceof ApiError)) {
    return {
      title: "Não foi possível enviar a mensagem",
      message: "Tente novamente ou verifique os logs do backend.",
      severity: "danger",
    };
  }

  const { status, detail } = error;
  const detailStr = detail || "";

  if (detailStr.includes("provider_http_429")) {
    return {
      title: "Limite temporário do provedor de IA atingido",
      message: "O Gemini retornou limite de uso/cota. Aguarde alguns minutos, verifique a cota no Google AI Studio ou use AI_PROVIDER=mock para continuar testando sem consumir API.",
      severity: "warning",
      technical: detailStr,
    };
  }
  if (detailStr.includes("ai_chat_disabled")) {
    return {
      title: "IA Chat desabilitado",
      message: "O módulo AI Chat está desabilitado no backend. Habilite ENABLE_AI_CHAT=true no runtime do app.",
      severity: "warning",
    };
  }
  if (status === 503 || detailStr.includes("ai_provider_configuration_error")) {
    return {
      title: "Provider de IA não configurado",
      message: "O backend não recebeu configuração válida do provider de IA.",
      severity: "danger",
      technical: detailStr,
    };
  }
  if (status === 502) {
    return {
      title: "Falha no provedor de IA",
      message: "O backend chamou o provider, mas a resposta externa falhou. Verifique logs do app.",
      severity: "danger",
      technical: detailStr,
    };
  }
  if (status === 401) {
    return {
      title: "Sessão expirada",
      message: "Entre novamente no sistema.",
      severity: "warning",
    };
  }
  if (status === 403) {
    return {
      title: "Sem permissão",
      message: "Seu usuário não tem permissão para usar este recurso.",
      severity: "danger",
    };
  }
  if (status === 404) {
    return {
      title: "Recurso não encontrado",
      message: "A conversa não foi encontrada ou o módulo está indisponível.",
      severity: "warning",
    };
  }

  return {
    title: "Não foi possível enviar a mensagem",
    message: "Tente novamente ou verifique os logs do backend.",
    severity: "danger",
    technical: detailStr,
  };
}

type RequestOptions = RequestInit & {
  token?: string | null;
  skipAuthRefresh?: boolean;
};

let refreshAccessToken: (() => Promise<string | null>) | null = null;
let handleUnauthorized: (() => void) | null = null;

export function configureApiAuth(options: {
  refreshAccessToken: () => Promise<string | null>;
  handleUnauthorized: () => void;
}) {
  refreshAccessToken = options.refreshAccessToken;
  handleUnauthorized = options.handleUnauthorized;
}

async function request<T>(path: string, init: RequestOptions = {}): Promise<T> {
  const { token, skipAuthRefresh, ...fetchInit } = init;
  const headers = new Headers(init.headers);
  const body = init.body;

  if (body && !(body instanceof FormData) && !headers.has("content-type")) {
    headers.set("content-type", "application/json");
  }

  async function execute(authToken: string | null | undefined) {
    const requestHeaders = new Headers(headers);
    if (authToken) {
      requestHeaders.set("authorization", `Bearer ${authToken}`);
    }
    return fetch(`${API_BASE}${path}`, {
      ...fetchInit,
      credentials: fetchInit.credentials ?? "include",
      headers: requestHeaders
    });
  }

  let response = await execute(token);

  if (response.status === 401 && !skipAuthRefresh && refreshAccessToken) {
    const nextToken = await refreshAccessToken().catch(() => null);
    if (nextToken) {
      response = await execute(nextToken);
    } else if (handleUnauthorized) {
      handleUnauthorized();
    }
  }

  if (!response.ok) {
    let detail: string | null = null;
    const responseText = await response.text().catch(() => "");
    if (responseText.trim()) {
      try {
        const json = JSON.parse(responseText) as { detail?: unknown };
        detail = normalizeErrorDetail(json.detail);
      } catch {
        detail = responseText;
      }
    }
    if (response.status === 401 && handleUnauthorized && !skipAuthRefresh) {
      handleUnauthorized();
    }
    throw new ApiError(detail || `API ${response.status}`, response.status, detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.headers.get("content-type")?.includes("application/json")) {
    return response.text() as Promise<T>;
  }

  return response.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
      skipAuthRefresh: true
    }),
  refresh: () => request<TokenResponse>("/auth/refresh", { method: "POST", skipAuthRefresh: true }),
  logout: (token?: string | null) => request<{ status: string }>("/auth/logout", { method: "POST", token, skipAuthRefresh: true }),
  me: (token: string) => request<User>("/auth/me", { token }),
  dashboardSummary: (token: string) => request<Record<string, number>>("/dashboard/summary", { token }),
  assetsByStatus: (token: string) => request<Array<{ status: string; count: number }>>("/dashboard/assets-by-status", { token }),
  recentMovements: (token: string) => request<Movement[]>("/dashboard/recent-movements", { token }),
  assets: (token: string, params = "") => {
    const query = params ? (params.startsWith("?") ? params : `?page_size=25${params.startsWith("&") ? params : `&${params}`}`) : "?page_size=25";
    return request<Page<Asset>>(`/assets${query}`, { token });
  },
  asset: (token: string, id: string) => request<Asset>(`/assets/${id}`, { token }),
  assetHistory: (token: string, id: string) => request<Movement[]>(`/assets/${id}/history`, { token }),
  moveAsset: (token: string, id: string, payload: Record<string, unknown>) =>
    request<Movement>(`/assets/${id}/move`, {
      method: "POST",
      body: JSON.stringify(payload),
      token
    }),
  createAsset: (token: string, payload: Record<string, unknown>) =>
    request<Asset>("/assets", { method: "POST", body: JSON.stringify(payload), token }),
  updateAsset: (token: string, id: string, payload: Record<string, unknown>) =>
    request<Asset>(`/assets/${id}`, { method: "PUT", body: JSON.stringify(payload), token }),
  deleteAsset: (token: string, id: string) => request<void>(`/assets/${id}`, { method: "DELETE", token }),
  users: (token: string, params = "") => {
    if (!params) {
      return request<Page<User>>("/users?page_size=25", { token });
    }
    const normalized = params.startsWith("?") ? params.slice(1) : params.replace(/^&/, "");
    if (normalized.includes("page_size=")) {
      return request<Page<User>>(`/users?${normalized}`, { token });
    }
    return request<Page<User>>(`/users?page_size=25&${normalized}`, { token });
  },
  user: (token: string, id: string) => request<User>(`/users/${id}`, { token }),
  createUser: (token: string, payload: Record<string, unknown>) =>
    request<User>("/users", { method: "POST", body: JSON.stringify(payload), token }),
  updateUser: (token: string, id: string, payload: Record<string, unknown>) =>
    request<User>(`/users/${id}`, { method: "PUT", body: JSON.stringify(payload), token }),
  deleteUser: (token: string, id: string) => request<void>(`/users/${id}`, { method: "DELETE", token }),
  userAssets: (token: string, id: string) => request<Asset[]>(`/users/${id}/assets`, { token }),
  globalSearch: (token: string, query: string) => request<SearchResponse>(`/search?q=${encodeURIComponent(query)}&limit=8`, { token }),
  audit: (token: string) => request<Page<AuditLog>>("/audit-logs?page_size=25", { token }),
  imports: (token: string) => request<Page<ImportJob>>("/imports?page_size=25", { token }),
  importUpload: (token: string, file: File, importMode = "INITIAL_LOAD") => {
    const form = new FormData();
    form.append("file", file);
    form.append("import_mode", importMode);
    return request<ImportJob>("/imports/spreadsheet/upload", {
      method: "POST",
      body: form,
      token
    });
  },
  importLansweeper: (token: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<ImportJob>("/imports/lansweeper", { method: "POST", body: form, token });
  },
  importPreview: (token: string, id: string) => request<ImportPreview>(`/imports/${id}/preview`, { token }),
  importStaging: (token: string, id: string) => request<Page<ImportStagingAsset>>(`/imports/${id}/staging?page_size=50`, { token }),
  importConflicts: (token: string, id: string) => request<ImportConflict[]>(`/imports/${id}/conflicts`, { token }),
  importValidationErrors: (token: string, id: string) => request<ImportValidationError[]>(`/imports/${id}/validation-errors`, { token }),
  updateImportMapping: (token: string, id: string, mapping: Record<string, string>, importMode?: string) =>
    request<ImportJob>(`/imports/${id}/mapping`, { method: "POST", body: JSON.stringify({ mapping, import_mode: importMode }), token }),
  applyImport: (token: string, id: string) => request<{ job: ImportJob; report: Record<string, unknown> }>(`/imports/${id}/apply`, { method: "POST", token }),
  cancelImport: (token: string, id: string) => request<ImportJob>(`/imports/${id}/cancel`, { method: "POST", token }),
  importReport: (token: string, id: string) => request<{ import_id: string; status: string; report: Record<string, unknown> }>(`/imports/${id}/report`, { token }),
  signaturePreview: (token: string, userId: string) =>
    request<string>(`/signatures/${userId}`, { token, headers: { "accept": "text/html" } }),
  signatureGenerate: (token: string, userId: string) =>
    request<string>(`/signatures/generate/${userId}`, {
      method: "POST",
      token,
      headers: { "accept": "text/html" }
    }),
  signatureDownloadHtml: (token: string, userId: string) =>
    request<string>(`/signatures/${userId}/download-html`, { token, headers: { "accept": "text/html" } }),
  macroTemplates: (token: string, params = "") => request<MacroTemplate[]>(`/macros/templates${params}`, { token }),
  macroRender: (token: string, payload: Record<string, unknown>) =>
    request<MacroRenderResponse>("/macros/render", { method: "POST", body: JSON.stringify(payload), token }),
  macroGenerate: (token: string, payload: Record<string, unknown>) =>
    request<MacroGeneration>("/macros/generate", { method: "POST", body: JSON.stringify(payload), token }),
  macroMarkCopied: (token: string, generationId: string) =>
    request<MacroGeneration>(`/macros/generations/${generationId}/copied`, { method: "POST", token }),
  macroAutocomplete: (token: string, query: string, hintType = "collaborator_name") =>
    request<MacroAutocompleteHint[]>(`/macros/autocomplete?q=${encodeURIComponent(query)}&hint_type=${encodeURIComponent(hintType)}`, { token }),
  suggestedMovementMacro: (token: string, movementId: string) =>
    request<SuggestedMovementMacro>(`/movements/${movementId}/suggested-macro`, { token }),
  aiChatHealth: (token: string) => request<AiChatProviderHealth>("/ai-chat/health", { token }),
  aiChatConversations: (token: string) => request<AiChatConversation[]>("/ai-chat/conversations", { token }),
  aiChatConversation: (token: string, id: string) => request<AiChatConversationDetail>(`/ai-chat/conversations/${id}`, { token }),
  aiChatCreateConversation: (token: string, payload: AiChatConversationCreate) =>
    request<AiChatConversationDetail>("/ai-chat/conversations", { method: "POST", body: JSON.stringify(payload), token }),
  aiChatSendMessage: (token: string, id: string, contentOrPayload: string | AiChatMessageCreate, mode?: AiChatMessageCreate["mode"]) => {
    const payload = typeof contentOrPayload === "string" ? { content: contentOrPayload, mode } : contentOrPayload;
    return request<AiChatConversationDetail>(`/ai-chat/conversations/${id}/messages`, { method: "POST", body: JSON.stringify(payload), token });
  }
};
