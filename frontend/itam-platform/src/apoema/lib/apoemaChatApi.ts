import { mockApoemaResponse } from "../mockApi";
import type {
  ApoemaAttachment,
  ApoemaChatAttachmentMeta,
  ApoemaChatRequest,
  ApoemaChatResponse,
  ApoemaProviderOption,
} from "../types";

const API_BASE = (import.meta.env.VITE_API_URL || "/api/v1").replace(/\/$/, "");

const DEFAULT_PROVIDER_OPTIONS: ApoemaProviderOption[] = [
  {
    id: "mock",
    label: "Mock/Fallback",
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

async function requestJson<T>(path: string, init: RequestInit = {}, token?: string | null): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("content-type")) {
    headers.set("content-type", "application/json");
  }
  if (token) {
    headers.set("authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: init.credentials ?? "include",
    headers,
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
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

export async function getAiProviders(token?: string | null): Promise<ApoemaProviderOption[]> {
  try {
    const response = await requestJson<{ providers: ApoemaProviderOption[] }>("/ai-chat/providers", {}, token);
    return response.providers.length > 0 ? response.providers : DEFAULT_PROVIDER_OPTIONS;
  } catch {
    return DEFAULT_PROVIDER_OPTIONS;
  }
}

export async function sendAiMessage(payload: ApoemaChatRequest, token?: string | null): Promise<ApoemaChatResponse> {
  try {
    return await requestJson<ApoemaChatResponse>(
      "/ai-chat/message",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      token,
    );
  } catch (error) {
    const attachments = toLocalAttachments(payload.attachments);
    const providerLabel = fallbackProviderLabel(payload.provider);
    const content = await mockApoemaResponse(payload.message, attachments, providerLabel);
    return {
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
      error: error instanceof Error ? error.message : "backend_unavailable",
    };
  }
}
