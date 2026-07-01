import { Copy } from "lucide-react";
import { useState } from "react";
import type { AiChatMessage } from "../types";

function roleLabel(role: AiChatMessage["role"]) {
  switch (role) {
    case "assistant":
      return "Apoema";
    case "system":
      return "Sistema";
    case "tool":
      return "Ferramenta";
    default:
      return "Você";
  }
}

function formatTimestamp(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function ChatMessage({ message }: { message: AiChatMessage }) {
  const [copied, setCopied] = useState(false);
  // source: "fallback" marks offline assistant messages.
  const isFallback = message.metadata?.source === "fallback" || message.metadata?.source === "apoema-local-fallback";
  const providerLabel = message.provider ? `${message.provider}${message.model ? ` • ${message.model}` : ""}` : null;

  async function copyMessage() {
    if (!message.content.trim() || !navigator.clipboard) {
      return;
    }
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  return (
    <article className={`apoema-chat-message role-${message.role} ${isFallback ? "is-fallback" : ""}`}>
      <div className="apoema-chat-message-head">
        <div className="apoema-chat-message-title">
          <strong>{roleLabel(message.role)}</strong>
          {providerLabel && <span>{providerLabel}</span>}
        </div>
        <div className="apoema-chat-message-meta">
          {isFallback && <span className="apoema-chat-message-source">Fallback local</span>}
          <span>{formatTimestamp(message.created_at)}</span>
        </div>
      </div>
      <p>{message.content}</p>
      <div className="apoema-chat-message-actions">
        <button type="button" className="apoema-ghost-button" onClick={() => void copyMessage()} disabled={!message.content.trim()}>
          <Copy size={14} />
          {copied ? "Copiado" : "Copiar"}
        </button>
      </div>
    </article>
  );
}
