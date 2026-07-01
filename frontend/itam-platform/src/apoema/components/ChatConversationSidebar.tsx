import { MessageSquarePlus, RotateCcw, ShieldAlert } from "lucide-react";
import type { AiChatConversation } from "../types";
import { StatusPill } from "./StatusPill";

type BannerTone = "warning" | "danger";

type SidebarBanner = {
  tone: BannerTone;
  title: string;
  message: string;
};

type Props = {
  conversations: AiChatConversation[];
  selectedConversationId: string | null;
  loading: boolean;
  state: "loading" | "ready" | "fallback" | "error";
  banner: SidebarBanner | null;
  fallbackNotice: string | null;
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void | Promise<void>;
  onReload: () => void | Promise<void>;
  creatingConversation?: boolean;
};

function formatConversationTime(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleString([], { month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export function ChatConversationSidebar({
  conversations,
  selectedConversationId,
  loading,
  state,
  banner,
  fallbackNotice,
  onSelectConversation,
  onNewConversation,
  onReload,
  creatingConversation = false,
}: Props) {
  return (
    <aside className="apoema-chat-sidebar apoema-panel">
      <div className="apoema-section-head">
        <div>
          <h2>Conversas</h2>
          <span>Backend-backed</span>
        </div>
        <div className="apoema-chat-sidebar-actions">
          <button type="button" className="apoema-ghost-button" onClick={() => void onReload()} disabled={loading}>
            <RotateCcw size={14} />
            Recarregar
          </button>
          <button type="button" className="apoema-primary-button" onClick={() => void onNewConversation()} disabled={creatingConversation}>
            <MessageSquarePlus size={14} />
            {creatingConversation ? "Criando..." : "Nova conversa"}
          </button>
        </div>
      </div>

      <div className="apoema-chat-sidebar-status">
        <StatusPill tone={state === "error" ? "warning" : state === "fallback" ? "warning" : state === "loading" ? "neutral" : "success"}>
          {state === "loading" ? "Carregando conversas" : state === "fallback" ? "Fallback local ativo" : state === "error" ? "Erro de conversas" : "Conversas do backend"}
        </StatusPill>
        {fallbackNotice ? <p>{fallbackNotice}</p> : <p>O histórico primário vem do backend e não de estado local.</p>}
      </div>

      {banner && (
        <div className={`apoema-warning ${banner.tone === "danger" ? "is-danger" : "is-warning"}`}>
          <ShieldAlert size={16} />
          <div>
            <strong>{banner.title}</strong>
            <p>{banner.message}</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="apoema-chat-empty-state">
          <strong>Carregando...</strong>
          <p>Buscando conversas do backend.</p>
        </div>
      ) : conversations.length === 0 ? (
        <div className="apoema-chat-empty-state">
          <strong>Nenhuma conversa ainda</strong>
          <p>Crie uma conversa nova para iniciar o chat com o backend.</p>
        </div>
      ) : (
        <div className="apoema-conversation-list" aria-label="Lista de conversas">
          {conversations.map((conversation) => {
            const active = conversation.id === selectedConversationId;
            const messageCount = conversation.messages?.length ?? 0;
            return (
              <button
                key={conversation.id}
                type="button"
                className={`apoema-conversation-item ${active ? "is-active" : ""}`}
                onClick={() => onSelectConversation(conversation.id)}
                aria-pressed={active}
              >
                <strong>{conversation.title || "Conversa sem título"}</strong>
                <span>
                  {conversation.provider}
                  {conversation.model ? ` • ${conversation.model}` : ""}
                </span>
                <small>
                  {messageCount} mensagem{messageCount === 1 ? "" : "s"}
                  {conversation.updated_at ? ` • ${formatConversationTime(conversation.updated_at)}` : ""}
                </small>
              </button>
            );
          })}
        </div>
      )}
    </aside>
  );
}
