import { ApoemaChatBridgeAdapter } from "@/apoema/adapters/ApoemaChatBridgeAdapter";

export type ChatSession = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type ChatMessage = {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

export type ChatMessagesPage = {
  messages: ChatMessage[];
  hasMore: boolean;
};

export const chatService = {
  async health(token: string) {
    return ApoemaChatBridgeAdapter.health(token);
  },

  async listSessions(token: string): Promise<ChatSession[]> {
    return ApoemaChatBridgeAdapter.listSessions(token);
  },

  async createSession(token: string, title = "Nova conversa"): Promise<ChatSession> {
    return ApoemaChatBridgeAdapter.createSession(token, title);
  },

  async renameSession(token: string, sessionId: string, title: string): Promise<void> {
    await ApoemaChatBridgeAdapter.renameSession(token, sessionId, title);
  },

  async deleteSession(token: string, sessionId: string): Promise<void> {
    await ApoemaChatBridgeAdapter.deleteSession(token, sessionId);
  },

  async getMessagesPage(
    token: string,
    sessionId: string,
    options?: { limit?: number; before?: { created_at: string; id: string } },
  ): Promise<ChatMessagesPage> {
    void options;
    const messages = await ApoemaChatBridgeAdapter.listMessages(token, sessionId);
    return { messages, hasMore: false };
  },

  async addMessage(token: string, sessionId: string, role: "user" | "assistant", content: string): Promise<ChatMessage> {
    const messages = await ApoemaChatBridgeAdapter.sendMessage(token, sessionId, { content });
    const lastMessage = messages.at(-1);
    if (!lastMessage) {
      throw new Error("Mensagem nao persistida no backend.");
    }
    return {
      id: lastMessage.id,
      session_id: lastMessage.session_id,
      role: role === "assistant" ? "assistant" : "user",
      content: lastMessage.content,
      created_at: lastMessage.created_at,
    };
  },

  async sendMessage(token: string, sessionId: string, content: string) {
    return ApoemaChatBridgeAdapter.sendMessage(token, sessionId, { content });
  },

  async createSessionAndSendMessage(token: string, title: string, content: string) {
    return ApoemaChatBridgeAdapter.createSessionAndSendMessage(token, title, { content });
  },
};
