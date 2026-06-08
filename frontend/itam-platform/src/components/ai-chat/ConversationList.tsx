import type { AiChatConversation } from "@/lib/types";

type Props = {
  conversations: AiChatConversation[];
  selectedId: string | null;
  loading?: boolean;
  onSelect: (id: string) => void;
  onNewConversation: () => void;
};

function providerLabel(conversation: AiChatConversation) {
  return `${conversation.provider}${conversation.model ? ` (${conversation.model})` : ""}`;
}

export function ConversationList({ conversations, selectedId, loading, onSelect, onNewConversation }: Props) {
  return (
    <aside className="ai-chat-sidebar card">
      <div className="ai-chat-sidebar-header">
        <h2>Conversas</h2>
        <button className="button primary" type="button" onClick={onNewConversation} disabled={loading}>
          Nova
        </button>
      </div>
      <div className="ai-chat-conversation-list">
        {conversations.length === 0 ? (
          <div className="ai-chat-empty-list-state">
            <strong>Nenhuma conversa ainda</strong>
            <p className="muted">Clique em "Nova" ou envie uma mensagem para iniciar o AI Chat.</p>
          </div>
        ) : null}
        {conversations.map((conversation) => {
          const title = conversation.title || "Nova conversa";
          return (
            <button
              className={conversation.id === selectedId ? "ai-chat-conversation active" : "ai-chat-conversation"}
              key={conversation.id}
              type="button"
              onClick={() => onSelect(conversation.id)}
              title={title}
            >
              <strong className="ai-chat-conversation-title">{title}</strong>
              {conversation.provider ? <span className="ai-chat-conversation-meta">{providerLabel(conversation)}</span> : null}
              <span className="ai-chat-conversation-date">{new Date(conversation.updated_at).toLocaleString("pt-BR")}</span>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
