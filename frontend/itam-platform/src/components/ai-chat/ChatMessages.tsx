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

export function ChatMessages({ messages, loading, onCopy }: Props) {
  return (
    <div className="ai-chat-messages" aria-live="polite">
      {messages.length === 0 ? (
        <div className="ai-chat-empty-messages">
          Envie uma mensagem ou use um preset acima.
        </div>
      ) : null}

      {messages.map((message) => (
        <article className={`ai-chat-message ${message.role}`} key={message.id}>
          <div className="ai-chat-message-body">
            <strong>{roleLabel(message.role)}</strong>
            <p>{message.content}</p>
          </div>
          {message.role === "assistant" ? (
            <button className="ai-chat-copy-button" type="button" onClick={() => onCopy(message.content)}>
              Copiar
            </button>
          ) : null}
        </article>
      ))}

      {loading ? (
        <div className="ai-chat-message assistant pending">
          <p>Gerando resposta...</p>
        </div>
      ) : null}
    </div>
  );
}
