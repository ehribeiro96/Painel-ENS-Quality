import type { ReactNode } from "react";

import { MessageSquarePlus, RotateCcw, Trash2 } from "lucide-react";

import type { AiChatConversation } from "@/lib/types";

type Props = {
  conversations: AiChatConversation[];
  hiddenConversations: AiChatConversation[];
  selectedId: string | null;
  loading?: boolean;
  onSelect: (id: string) => void;
  onNewConversation: () => void;
  onHideConversation: (id: string) => void;
  onRestoreConversation: (id: string) => void;
};

function providerLabel(conversation: AiChatConversation) {
  return `${conversation.provider}${conversation.model ? ` (${conversation.model})` : ""}`;
}

function formatConversationDate(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function ConversationCard({
  conversation,
  selected,
  actionLabel,
  actionIcon,
  onSelect,
  onAction,
  actionDisabled,
}: {
  conversation: AiChatConversation;
  selected: boolean;
  actionLabel: string;
  actionIcon: ReactNode;
  onSelect: () => void;
  onAction: () => void;
  actionDisabled?: boolean;
}) {
  return (
    <div className={selected ? "ai-chat-conversation-card active" : "ai-chat-conversation-card"}>
      <button className="ai-chat-conversation-main" type="button" onClick={onSelect}>
        <strong className="ai-chat-conversation-title">{conversation.title || "Nova conversa"}</strong>
        <span className="ai-chat-conversation-meta">{providerLabel(conversation)}</span>
        <span className="ai-chat-conversation-date">{formatConversationDate(conversation.updated_at)}</span>
      </button>
      <button className="ai-chat-conversation-action" type="button" onClick={onAction} disabled={actionDisabled} aria-label={actionLabel} title={actionLabel}>
        {actionIcon}
      </button>
    </div>
  );
}

export function ConversationList({
  conversations,
  hiddenConversations,
  selectedId,
  loading,
  onSelect,
  onNewConversation,
  onHideConversation,
  onRestoreConversation,
}: Props) {
  return (
    <aside className="ai-chat-sidebar card">
      <div className="ai-chat-sidebar-header">
        <div>
          <p className="ai-chat-sidebar-eyebrow">Histórico local</p>
          <h2>Conversas</h2>
        </div>
        <button className="button primary" type="button" onClick={onNewConversation} disabled={loading}>
          <MessageSquarePlus size={16} />
          Nova
        </button>
      </div>

      <div className="ai-chat-sidebar-summary">
        <span>{conversations.length} visíveis</span>
        <span>{hiddenConversations.length} ocultas localmente</span>
      </div>

      <div className="ai-chat-conversation-list">
        {conversations.length === 0 ? (
          <div className="ai-chat-empty-list-state">
            <strong>Nenhuma conversa visível</strong>
            <p className="muted">Crie uma nova conversa ou restaure uma conversa oculta localmente.</p>
          </div>
        ) : null}

        {conversations.map((conversation) => (
          <ConversationCard
            key={conversation.id}
            conversation={conversation}
            selected={conversation.id === selectedId}
            actionLabel={`Ocultar ${conversation.title || "conversa"}`}
            actionIcon={<Trash2 size={16} />}
            onSelect={() => onSelect(conversation.id)}
            onAction={() => onHideConversation(conversation.id)}
            actionDisabled={loading}
          />
        ))}
      </div>

      {hiddenConversations.length > 0 ? (
        <div className="ai-chat-hidden-section">
          <div className="ai-chat-hidden-header">
            <strong>Ocultas localmente</strong>
            <span className="muted">não foram apagadas no backend</span>
          </div>
          <div className="ai-chat-conversation-list compact">
            {hiddenConversations.map((conversation) => (
              <ConversationCard
                key={conversation.id}
                conversation={conversation}
                selected={false}
                actionLabel={`Restaurar ${conversation.title || "conversa"}`}
                actionIcon={<RotateCcw size={16} />}
                onSelect={() => onSelect(conversation.id)}
                onAction={() => onRestoreConversation(conversation.id)}
                actionDisabled={loading}
              />
            ))}
          </div>
        </div>
      ) : null}
    </aside>
  );
}
