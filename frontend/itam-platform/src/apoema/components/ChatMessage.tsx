import type { ApoemaMessage } from "../types";

export function ChatMessage({ message }: { message: ApoemaMessage }) {
  return (
    <article className={`apoema-chat-message role-${message.role}`}>
      <div className="apoema-chat-message-head">
        <strong>{message.role === "assistant" ? "Apoema" : message.role === "system" ? "Sistema" : "Você"}</strong>
        <span>{message.time}</span>
      </div>
      <p>{message.content}</p>
      {message.attachments && message.attachments.length > 0 && (
        <div className="apoema-chat-attachments">
          {message.attachments.map((attachment) => (
            <span key={attachment.id} className="apoema-attachment-chip">
              {attachment.name}
            </span>
          ))}
        </div>
      )}
    </article>
  );
}
