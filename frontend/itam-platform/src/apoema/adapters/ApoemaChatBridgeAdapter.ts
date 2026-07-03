import { api } from "@/lib/api";
import type {
  AiChatConversation,
  AiChatConversationCreate,
  AiChatConversationDetail,
  AiChatConversationUpdate,
  AiChatMessage,
  AiChatMessageCreate,
  AiChatProviderHealth,
} from "@/lib/types";

export type ApoemaChatSession = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type ApoemaChatMessage = {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

export type ApoemaChatMessagePayload = {
  content: string;
  mode?: AiChatMessageCreate["mode"] | null;
};

function normalizeSession(conversation: AiChatConversation): ApoemaChatSession {
  return {
    id: conversation.id,
    title: conversation.title ?? "Nova conversa",
    created_at: conversation.created_at,
    updated_at: conversation.updated_at,
  };
}

function normalizeMessage(message: AiChatMessage): ApoemaChatMessage {
  return {
    id: message.id,
    session_id: message.conversation_id,
    role: message.role === "assistant" ? "assistant" : "user",
    content: message.content,
    created_at: message.created_at,
  };
}

export const ApoemaChatBridgeAdapter = {
  async health(token: string): Promise<AiChatProviderHealth> {
    return api.aiChatHealth(token);
  },

  async listSessions(token: string): Promise<ApoemaChatSession[]> {
    const items = await api.aiChatConversations(token);
    return items
      .map(normalizeSession)
      .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
  },

  async createSession(token: string, title = "Nova conversa"): Promise<ApoemaChatSession> {
    const conversation = await api.aiChatCreateConversation(token, { title } satisfies AiChatConversationCreate);
    return normalizeSession(conversation);
  },

  async renameSession(token: string, sessionId: string, title: string): Promise<void> {
    await api.aiChatUpdateConversation(token, sessionId, { title } satisfies AiChatConversationUpdate);
  },

  async deleteSession(token: string, sessionId: string): Promise<void> {
    await api.aiChatDeleteConversation(token, sessionId);
  },

  async listMessages(token: string, sessionId: string): Promise<ApoemaChatMessage[]> {
    const conversation = await api.aiChatConversation(token, sessionId);
    return (conversation.messages ?? []).map(normalizeMessage);
  },

  async sendMessage(token: string, sessionId: string, payload: ApoemaChatMessagePayload): Promise<ApoemaChatMessage[]> {
    const conversation = await api.aiChatSendMessage(token, sessionId, {
      content: payload.content,
      mode: payload.mode ?? null,
    } satisfies AiChatMessageCreate);
    return (conversation.messages ?? []).map(normalizeMessage);
  },

  async createSessionAndSendMessage(
    token: string,
    title: string,
    payload: ApoemaChatMessagePayload,
  ): Promise<{ session: ApoemaChatSession; messages: ApoemaChatMessage[] }> {
    const conversation = await api.aiChatCreateConversation(token, {
      title,
      message: payload.content,
      mode: payload.mode ?? null,
    } satisfies AiChatConversationCreate);
    return {
      session: normalizeSession(conversation),
      messages: (conversation.messages ?? []).map(normalizeMessage),
    };
  },

  normalizeSession,
  normalizeMessage,
};
