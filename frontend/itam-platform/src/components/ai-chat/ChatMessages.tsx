import { Bot, Copy, UserRound } from "lucide-react";

import type { AiChatMessage } from "@/lib/types";

type Props = {
  messages: AiChatMessage[];
  loading?: boolean;
  onCopy: (content: string) => void;
};

function roleLabel(role: AiChatMessage["role"]) {
  if (role === "user") {
    return "Você";
  }
  if (role === "assistant") {
    return "IA";
  }
  return "Sistema";
}

function roleIcon(role: AiChatMessage["role"]) {
  if (role === "assistant") {
    return <Bot size={16} />;
  }
  return <UserRound size={16} />;
}

function formatMessageDate(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

export function ChatMessages({ messages, loading, onCopy }: Props) {
  return (
    <div className="ai-chat-messages" aria-live="polite" role="log">
      {messages.length === 0 ? (
        <div className="ai-chat-empty-messages">
          <strong>Sem mensagens ainda</strong>
          <p>Envie uma mensagem ou use um preset acima para iniciar a conversa.</p>
        </div>
      ) : null}

      {messages.map((message) => (
        <article className={`ai-chat-message ${message.role}`} key={message.id}>
          <header className="ai-chat-message-header">
            <span className="ai-chat-message-role">
              {roleIcon(message.role)}
              {roleLabel(message.role)}
            </span>
            <time dateTime={message.created_at} className="ai-chat-message-date">
              {formatMessageDate(message.created_at)}
            </time>
          </header>
          <div className="ai-chat-message-body">
            <p>{message.content}</p>
          </div>
          {message.role === "assistant" ? (
            <button className="ai-chat-copy-button" type="button" onClick={() => onCopy(message.content)}>
              <Copy size={14} />
              Copiar
            </button>
          ) : null}
        </article>
      ))}

      {loading ? (
        <div className="ai-chat-message assistant pending">
          <header className="ai-chat-message-header">
            <span className="ai-chat-message-role">
              <Bot size={16} />
              IA
            </span>
          </header>
          <p>Gerando resposta...</p>
        </div>
      ) : null}
    </div>
  );
}
