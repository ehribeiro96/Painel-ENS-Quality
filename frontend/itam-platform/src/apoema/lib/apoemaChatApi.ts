import { mockApoemaResponse } from "../mockApi";
import { ApoemaApiError } from "../types";
import type {
  ApoemaAttachment,
  ApoemaApiErrorKind,
  ApoemaChatAttachmentMeta,
  ApoemaChatMessageResult,
  ApoemaChatRequest,
  ApoemaChatResponse,
  ApoemaProviderLoadResult,
  ApoemaProviderOption,
} from "../types";

const API_BASE = (import.meta.env.VITE_API_URL || "/api/v1").replace(/\/$/, "");

const DEFAULT_PROVIDER_OPTIONS: ApoemaProviderOption[] = [
  {
    id: "mock",
    label: "Mock adapter",
    status: "online",
    models: ["fallback-local"],
    default_model: "fallback-local",
  },
  {
    id: "ollama",
    label: "Ollama",
    status: "offline",
    models: ["qwen3:4b-64k", "qwen2.5-coder:7b"],
    default_model: "qwen3:4b-64k",
  },
  {
    id: "hermes",
    label: "Hermes",
    status: "unconfigured",
    models: ["hermes-agent"],
    default_model: "hermes-agent",
  },
];

function classifyStatus(status: number): ApoemaApiErrorKind {
  if (status === 401) {
    return "auth_required";
  }
  if (status === 403) {
    return "forbidden";
  }
  if (status === 429) {
    return "rate_limited";
  }
  if (status === 422) {
    return "validation_error";
  }
  if (status >= 500 && status < 600) {
    return "backend_error";
  }
  return "unknown_api_error";
}

function normalizeDetail(value: unknown): string | null {
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

function extractErrorMessage(details: unknown, status: number): string {
  if (typeof details === "string" && details.trim()) {
    return details;
  }
  if (details && typeof details === "object" && "detail" in details) {
    const detail = normalizeDetail((details as { detail?: unknown }).detail);
    if (detail) {
      return detail;
    }
  }
  return `API ${status}`;
}

function buildApiError(response: Response, details: unknown): ApoemaApiError {
  return new ApoemaApiError(extractErrorMessage(details, response.status), classifyStatus(response.status), response.status, details);
}

async function requestJson<T>(path: string, init: RequestInit = {}, token?: string | null): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("content-type")) {
    headers.set("content-type", "application/json");
  }
  if (token) {
    headers.set("authorization", `Bearer ${token}`);
  }

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      credentials: init.credentials ?? "include",
      headers,
    });

    if (!response.ok) {
      const rawText = await response.text().catch(() => "");
      let details: unknown = rawText || null;
      if (rawText.trim() && (response.headers.get("content-type") ?? "").includes("application/json")) {
        try {
          details = JSON.parse(rawText) as unknown;
        } catch {
          details = rawText;
        }
      }
      throw buildApiError(response, details);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    const contentType = response.headers.get("content-type") ?? "";
    if (!contentType.includes("application/json")) {
      return response.text() as Promise<T>;
    }

    try {
      return (await response.json()) as T;
    } catch (error) {
      throw new ApoemaApiError("Resposta inválida do backend.", "unknown_api_error", response.status, error);
    }
  } catch (error) {
    if (error instanceof ApoemaApiError) {
      throw error;
    }
    throw new ApoemaApiError("Backend indisponível por falha de rede.", "network_unavailable", undefined, error);
  }
}

function toLocalAttachments(attachments: ApoemaChatAttachmentMeta[]): ApoemaAttachment[] {
  return attachments.map((attachment) => ({
    id: attachment.id,
    name: attachment.name,
    size: `${attachment.size} B`,
    sizeBytes: attachment.size,
    mimeType: attachment.mime_type,
    kind: attachment.kind,
    sensitive: attachment.sensitive,
  }));
}

function fallbackProviderLabel(providerId: string) {
  return DEFAULT_PROVIDER_OPTIONS.find((provider) => provider.id === providerId)?.label ?? providerId;
}

function fallbackId(prefix: string) {
  const uuid = globalThis.crypto?.randomUUID?.();
  return uuid ? `${prefix}-${uuid}` : `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export async function getAiProviders(token?: string | null): Promise<ApoemaProviderLoadResult> {
  try {
    const response = await requestJson<{ providers: ApoemaProviderOption[] }>("/ai-chat/providers", {}, token);
    return {
      kind: "online",
      providers: response.providers,
    };
  } catch (error) {
    if (error instanceof ApoemaApiError && error.kind === "network_unavailable") {
      return {
        kind: "fallback",
        providers: DEFAULT_PROVIDER_OPTIONS,
        offline: true,
        notice: "Backend indisponível. Exibindo catálogo local de fallback.",
      };
    }
    throw error;
  }
}

export async function sendAiMessage(payload: ApoemaChatRequest, token?: string | null): Promise<ApoemaChatMessageResult> {
  try {
    const response = await requestJson<ApoemaChatResponse>(
      "/ai-chat/message",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      token,
    );
    return {
      kind: "online",
      response,
    };
  } catch (error) {
    if (error instanceof ApoemaApiError && error.kind === "network_unavailable") {
      const attachments = toLocalAttachments(payload.attachments);
      const providerLabel = fallbackProviderLabel(payload.provider);
      const content = await mockApoemaResponse(payload.message, attachments, providerLabel);
      return {
        kind: "fallback",
        offline: true,
        notice: "Backend indisponível. Exibindo resposta local de fallback.",
        response: {
          conversation_id: payload.conversation_id ?? fallbackId("fallback-conversation"),
          message_id: fallbackId("fallback-message"),
          provider: payload.provider,
          model: payload.model,
          status: "offline",
          content,
          created_at: new Date().toISOString(),
          usage: {
            prompt_tokens: null,
            completion_tokens: null,
            total_tokens: null,
          },
          error: "network_unavailable",
        },
      };
    }
    throw error;
  }
}
