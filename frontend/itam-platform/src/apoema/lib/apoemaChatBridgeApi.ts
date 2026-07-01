import { apoemaConversations, apoemaInitialMessages } from "../data";
import { AiChatApiError, ApoemaApiError } from "../types";
import type {
  AiChatConversation,
  AiChatConversationCreate,
  AiChatErrorCode,
  AiChatHealth,
  AiChatMessage,
  AiChatProvider,
  AiChatProviderId,
  AiChatSendMessageRequest,
  AiChatSendMessageResponse,
  ApoemaProviderLoadResult,
} from "../types";

const API_BASE = "/api/v1";

export const AI_CHAT_PROVIDER_FALLBACK_OPTIONS: AiChatProvider[] = [
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

type RequestOptions = RequestInit & {
  token?: string | null;
};

type ConversationDetail = AiChatConversation & {
  messages: AiChatMessage[];
};

type ConversationResult =
  | {
      kind: "online";
      conversation: ConversationDetail;
    }
  | {
      kind: "fallback";
      conversation: ConversationDetail;
      offline: true;
      notice: string;
    };

type ConversationListResult =
  | {
      kind: "online";
      conversations: AiChatConversation[];
    }
  | {
      kind: "fallback";
      conversations: AiChatConversation[];
      offline: true;
      notice: string;
    };

type AiChatMessageResponseResult =
  | {
      kind: "online";
      response: AiChatSendMessageResponse;
    }
  | {
      kind: "fallback";
      response: AiChatSendMessageResponse;
      offline: true;
      notice: string;
    };

const fallbackConversationStore = new Map<string, ConversationDetail>();

function buildFallbackStore() {
  if (fallbackConversationStore.size > 0) {
    return;
  }

  apoemaConversations.forEach((conversation, index) => {
    const conversationId = conversation.id;
    const messages: AiChatMessage[] =
      index === 0
        ? apoemaInitialMessages.map((message, messageIndex) => ({
            id: `${conversationId}-fallback-${messageIndex + 1}`,
            conversation_id: conversationId,
            role: message.role,
            content: message.content,
            provider: "mock",
            model: "fallback-local",
            metadata: {
              source: "apoema-local-fallback",
              origin: "seed",
            },
            created_at: new Date(Date.now() - (35 - messageIndex * 3) * 60_000).toISOString(),
          }))
        : index === 1
          ? [
              {
                id: `${conversationId}-fallback-1`,
                conversation_id: conversationId,
                role: "user",
                content: "Consolide o plano de importação com validação de placeholders.",
                provider: "mock",
                model: "fallback-local",
                metadata: {
                  source: "apoema-local-fallback",
                  origin: "seed",
                },
                created_at: new Date(Date.now() - 24 * 60_000).toISOString(),
              },
              {
                id: `${conversationId}-fallback-2`,
                conversation_id: conversationId,
                role: "assistant",
                content:
                  "Plano resumido: validar arquivo, sinalizar campos obrigatórios, confirmar permissões e só então iniciar a importação supervisionada.",
                provider: "mock",
                model: "fallback-local",
                metadata: {
                  source: "apoema-local-fallback",
                  origin: "seed",
                },
                created_at: new Date(Date.now() - 20 * 60_000).toISOString(),
              },
            ]
          : [
              {
                id: `${conversationId}-fallback-1`,
                conversation_id: conversationId,
                role: "assistant",
                content: "Revisão de SLA em andamento. Foque nos chamados críticos e no prazo de resposta.",
                provider: "mock",
                model: "fallback-local",
                metadata: {
                  source: "apoema-local-fallback",
                  origin: "seed",
                },
                created_at: new Date(Date.now() - 14 * 60_000).toISOString(),
              },
            ];

    fallbackConversationStore.set(conversationId, {
      id: conversationId,
      user_id: "00000000-0000-0000-0000-000000000000",
      title: conversation.title,
      provider: "mock",
      model: "fallback-local",
      system_prompt_version: "apoema-m8b-fallback",
      metadata: {
        subject: conversation.subject,
        source: "apoema-local-fallback",
      },
      created_at: new Date(Date.now() - (48 - index * 9) * 60_000).toISOString(),
      updated_at: new Date(Date.now() - (40 - index * 7) * 60_000).toISOString(),
      messages,
    });
  });
}

buildFallbackStore();

function fallbackId(prefix: string) {
  const uuid = globalThis.crypto?.randomUUID?.();
  return uuid ? `${prefix}-${uuid}` : `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function cloneMessage(message: AiChatMessage): AiChatMessage {
  return {
    ...message,
    metadata: { ...message.metadata },
  };
}

function cloneConversation(conversation: ConversationDetail): ConversationDetail {
  return {
    ...conversation,
    metadata: { ...conversation.metadata },
    messages: conversation.messages.map((message) => cloneMessage(message)),
  };
}

function listFallbackConversations(): AiChatConversation[] {
  return Array.from(fallbackConversationStore.values()).map(({ messages: _messages, ...conversation }) => ({
    ...conversation,
    metadata: { ...conversation.metadata },
  }));
}

function getFallbackConversation(conversationId: string): ConversationDetail | null {
  const conversation = fallbackConversationStore.get(conversationId);
  return conversation ? cloneConversation(conversation) : null;
}

function ensureFallbackConversation(conversationId: string, title?: string | null): ConversationDetail {
  const existing = fallbackConversationStore.get(conversationId);
  if (existing) {
    return cloneConversation(existing);
  }

  const createdAt = new Date().toISOString();
  const conversation: ConversationDetail = {
    id: conversationId,
    user_id: "00000000-0000-0000-0000-000000000000",
    title: title ?? "Conversa sem título",
    provider: "mock",
    model: "fallback-local",
    system_prompt_version: "apoema-m8b-fallback",
    metadata: {
      source: "apoema-local-fallback",
      origin: "runtime",
    },
    created_at: createdAt,
    updated_at: createdAt,
    messages: [],
  };

  fallbackConversationStore.set(conversationId, cloneConversation(conversation));
  return cloneConversation(conversation);
}

function fallbackConversationTitle(message: string) {
  const normalized = message.trim().replace(/\s+/g, " ");
  if (!normalized) {
    return "Nova conversa";
  }
  return normalized.length > 54 ? `${normalized.slice(0, 51).trimEnd()}...` : normalized;
}

function fallbackConversationReply(content: string, provider: AiChatProviderId, model: string) {
  const normalized = content.trim();
  return normalized
    ? `Backend indisponível. Exibindo resposta local de fallback. Recebi: "${normalized}". O conector ${provider} (${model}) continua sob controle local para validação da interface.`
    : `Backend indisponível. Exibindo resposta local de fallback. O conector ${provider} (${model}) continua sob controle local para validação da interface.`;
}

function classifyStatus(status: number): AiChatErrorCode {
  if (status === 401) return "auth_required";
  if (status === 403) return "forbidden";
  if (status === 404) return "not_found";
  if (status === 410) return "expired";
  if (status === 422) return "validation_error";
  if (status === 429) return "rate_limited";
  if (status >= 500 && status < 600) return "backend_error";
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

function extractMessage(details: unknown, status: number): string {
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

function buildApiError(response: Response, details: unknown) {
  return new AiChatApiError(extractMessage(details, response.status), classifyStatus(response.status), response.status, details);
}

async function requestJson<T>(path: string, init: RequestOptions = {}, token?: string | null): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("content-type")) {
    headers.set("content-type", "application/json");
  }
  if (token) {
    headers.set("authorization", `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      credentials: init.credentials ?? "include",
      headers,
    });
  } catch (error) {
    throw new AiChatApiError("Backend indisponível por falha de rede.", "network_unavailable", undefined, error);
  }

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
    throw new AiChatApiError("Resposta inválida do backend.", "unknown_api_error", response.status, error);
  }
}

function isNetworkUnavailable(error: unknown) {
  return error instanceof ApoemaApiError && error.kind === "network_unavailable";
}

export async function getAiChatHealth(token?: string | null): Promise<AiChatHealth> {
  return requestJson<AiChatHealth>("/ai-chat/health", {}, token);
}

export async function getAiChatProviders(token?: string | null): Promise<ApoemaProviderLoadResult> {
  try {
    const response = await requestJson<{ providers: AiChatProvider[] }>("/ai-chat/providers", {}, token);
    return {
      kind: "online",
      providers: response.providers,
    };
  } catch (error) {
    if (isNetworkUnavailable(error)) {
      return {
        kind: "fallback",
        providers: AI_CHAT_PROVIDER_FALLBACK_OPTIONS,
        offline: true,
        notice: "Backend indisponível. Exibindo catálogo local de fallback.",
      };
    }
    throw error;
  }
}

export async function listAiChatConversations(token?: string | null): Promise<ConversationListResult> {
  try {
    const conversations = await requestJson<AiChatConversation[]>("/ai-chat/conversations", {}, token);
    return {
      kind: "online",
      conversations,
    };
  } catch (error) {
    if (isNetworkUnavailable(error)) {
      return {
        kind: "fallback",
        conversations: listFallbackConversations(),
        offline: true,
        notice: "Backend indisponível. Exibindo histórico local de fallback.",
      };
    }
    throw error;
  }
}

export async function createAiChatConversation(payload: AiChatConversationCreate, token?: string | null): Promise<ConversationResult> {
  try {
    const conversation = await requestJson<AiChatConversation>("/ai-chat/conversations", {
      method: "POST",
      body: JSON.stringify(payload),
    }, token);

    return {
      kind: "online",
      conversation: {
        ...conversation,
        messages: conversation.messages ? conversation.messages.map((message) => cloneMessage(message)) : [],
      },
    };
  } catch (error) {
    if (isNetworkUnavailable(error)) {
      const conversationId = fallbackId("apoema-chat-fallback");
      const detail = ensureFallbackConversation(conversationId, payload.title ?? fallbackConversationTitle(payload.message ?? ""));
      if (payload.message?.trim()) {
        return appendFallbackConversationMessage(detail.id, payload.message, "mock", "fallback-local", "Nova conversa criada em modo de fallback local.");
      }

      return {
        kind: "fallback",
        conversation: detail,
        offline: true,
        notice: "Backend indisponível. Exibindo conversa local de fallback.",
      };
    }
    throw error;
  }
}

export async function getAiChatConversation(conversationId: string, token?: string | null): Promise<ConversationResult | null> {
  try {
    const conversation = await requestJson<AiChatConversation>(`/ai-chat/conversations/${encodeURIComponent(conversationId)}`, {}, token);
    const messages = conversation.messages ? conversation.messages.map((message) => cloneMessage(message)) : [];
    return {
      kind: "online",
      conversation: {
        ...conversation,
        messages,
      },
    };
  } catch (error) {
    if (isNetworkUnavailable(error)) {
      const detail = getFallbackConversation(conversationId);
      if (detail) {
        return {
          kind: "fallback",
          conversation: detail,
          offline: true,
          notice: "Backend indisponível. Exibindo conversa local de fallback.",
        };
      }
      return null;
    }
    throw error;
  }
}

function appendFallbackConversationMessage(
  conversationId: string,
  content: string,
  provider: AiChatProviderId,
  model: string,
  notice: string,
): ConversationResult {
  const current = ensureFallbackConversation(conversationId);
  const now = new Date().toISOString();
  const nextMessages: AiChatMessage[] = [
    ...current.messages,
    {
      id: `${conversationId}-user-${current.messages.length + 1}`,
      conversation_id: conversationId,
      role: "user",
      content,
      provider,
      model,
      metadata: {
        source: "apoema-local-fallback",
        origin: "runtime",
        status: "fallback",
      },
      created_at: now,
    },
    {
      id: `${conversationId}-assistant-${current.messages.length + 2}`,
      conversation_id: conversationId,
      role: "assistant",
      content: fallbackConversationReply(content, provider, model),
      provider,
      model,
      metadata: {
        source: "apoema-local-fallback",
        origin: "runtime",
        status: "fallback",
      },
      created_at: new Date(Date.now() + 1000).toISOString(),
    },
  ];

  const conversation: ConversationDetail = {
    ...current,
    updated_at: now,
    messages: nextMessages,
  };
  fallbackConversationStore.set(conversationId, cloneConversation(conversation));

  return {
    kind: "fallback",
    conversation,
    offline: true,
    notice,
  };
}

export async function sendAiChatConversationMessage(
  conversationId: string,
  payload: { content: string; mode?: string | null },
  token?: string | null,
): Promise<ConversationResult> {
  try {
    const conversation = await requestJson<AiChatConversation>(
      `/ai-chat/conversations/${encodeURIComponent(conversationId)}/messages`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      token,
    );
    return {
      kind: "online",
      conversation: {
        ...conversation,
        messages: conversation.messages ? conversation.messages.map((message) => cloneMessage(message)) : [],
      },
    };
  } catch (error) {
    if (isNetworkUnavailable(error)) {
      return appendFallbackConversationMessage(
        conversationId,
        payload.content,
        "mock",
        "fallback-local",
        "Backend indisponível. Exibindo conversa local de fallback.",
      );
    }
    throw error;
  }
}

export async function sendAiChatMessage(payload: AiChatSendMessageRequest, token?: string | null): Promise<AiChatMessageResponseResult> {
  try {
    const response = await requestJson<AiChatSendMessageResponse>("/ai-chat/message", {
      method: "POST",
      body: JSON.stringify(payload),
    }, token);
    return {
      kind: "online",
      response,
    };
  } catch (error) {
    if (isNetworkUnavailable(error)) {
      const response: AiChatSendMessageResponse = {
        conversation_id: payload.conversation_id ?? fallbackId("apoema-chat-message"),
        message_id: fallbackId("apoema-chat-message"),
        provider: payload.provider,
        model: payload.model,
        status: "offline",
        content: fallbackConversationReply(payload.message, payload.provider, payload.model),
        created_at: new Date().toISOString(),
        usage: {
          prompt_tokens: null,
          completion_tokens: null,
          total_tokens: null,
        },
        error: null,
      };
      return {
        kind: "fallback",
        response,
        offline: true,
        notice: "Backend indisponível. Exibindo resposta local de fallback.",
      };
    }
    throw error;
  }
}

export type { ConversationDetail as AiChatConversationDetail };
export type { ConversationListResult as AiChatConversationListResult };
export type { ConversationResult as AiChatConversationMutationResult };
