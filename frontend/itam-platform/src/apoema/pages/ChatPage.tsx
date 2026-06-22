import { useMemo, useState } from "react";
import { AlertTriangle, Paperclip, ShieldAlert, Sparkles } from "lucide-react";
import { ChatComposer } from "../components/ChatComposer";
import { ChatMessage } from "../components/ChatMessage";
import { FileDropzone } from "../components/FileDropzone";
import { StatusPill } from "../components/StatusPill";
import { apoemaConversations, apoemaInitialMessages } from "../data";
import { attachmentWarning, mockApoemaResponse } from "../mockApi";
import type { ApoemaAttachment, ApoemaMessage } from "../types";

function humanSize(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  const kb = bytes / 1024;
  return `${kb.toFixed(kb >= 10 ? 0 : 1)} KB`;
}

function toAttachment(file: File): ApoemaAttachment {
  return {
    id: `${file.name}-${file.size}-${file.lastModified}`,
    name: file.name,
    size: humanSize(file.size),
    kind: file.type || "unknown",
    sensitive: /\.(env|pem|key|sqlite|db|sql)$/i.test(file.name)
  };
}

export function ChatPage() {
  const [conversationId, setConversationId] = useState(apoemaConversations[0]?.id ?? "");
  const [messages, setMessages] = useState<ApoemaMessage[]>(apoemaInitialMessages);
  const [prompt, setPrompt] = useState("");
  const [attachments, setAttachments] = useState<ApoemaAttachment[]>([]);
  const [busy, setBusy] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [provider, setProvider] = useState("Ollama mock");

  const warning = useMemo(() => attachmentWarning(attachments), [attachments]);

  async function sendMessage() {
    if (busy) return;
    const content = prompt.trim();
    if (!content && attachments.length === 0) {
      return;
    }

    const userMessage: ApoemaMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: content || "Anexei arquivos para revisão.",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      attachments
    };

    setMessages((current) => [...current, userMessage]);
    setPrompt("");
    setBusy(true);

    const reply = await mockApoemaResponse(content, attachments, provider);
    setMessages((current) => [
      ...current,
      {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: reply,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      }
    ]);
    setAttachments([]);
    setBusy(false);
  }

  function addFiles(files: File[]) {
    const mapped = files.map(toAttachment);
    setAttachments((current) => [...current, ...mapped]);
  }

  return (
    <div className="apoema-chat-layout">
      <aside className="apoema-chat-sidebar apoema-panel">
        <div className="apoema-section-head">
          <h2>Conversations</h2>
          <span>Workspace</span>
        </div>
        <div className="apoema-conversation-list">
          {apoemaConversations.map((conversation) => (
            <button
              key={conversation.id}
              type="button"
              className={`apoema-conversation-item ${conversation.id === conversationId ? "is-active" : ""}`}
              onClick={() => setConversationId(conversation.id)}
            >
              <strong>{conversation.title}</strong>
              <span>{conversation.subject}</span>
              <small>{conversation.updatedAt}</small>
            </button>
          ))}
        </div>
        <div className="apoema-chat-sidebar-card">
          <StatusPill tone="success">
            <Sparkles size={14} />
            IA habilitada
          </StatusPill>
          <p>Este espaço usa adaptadores mockados para demonstrar o fluxo sem expor dados reais.</p>
        </div>
      </aside>

      <section className="apoema-panel apoema-chat-main">
        <div className="apoema-section-head">
          <div>
            <StatusPill tone="info">Assistente Apoema</StatusPill>
            <h1>Como posso ajudar?</h1>
          </div>
          <label className="apoema-provider-select">
            Provedor
            <select value={provider} onChange={(event) => setProvider(event.target.value)}>
              <option>Ollama mock</option>
              <option>OpenAI mock</option>
              <option>Router corporativo</option>
            </select>
          </label>
        </div>

        <div className="apoema-chat-messages" aria-live="polite">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
        </div>

        <div className="apoema-chat-dock">
          <FileDropzone
            dragging={dragging}
            onDragStateChange={setDragging}
            onFiles={addFiles}
            label="Arraste e solte arquivos para anexar ao contexto"
          />

          {warning && (
            <div className="apoema-warning">
              <AlertTriangle size={16} />
              <div>
                <strong>{warning.title}</strong>
                <p>{warning.description}</p>
              </div>
            </div>
          )}

          {attachments.length > 0 && (
            <div className="apoema-attachment-list">
              {attachments.map((attachment) => (
                <span key={attachment.id} className="apoema-attachment-chip">
                  <Paperclip size={14} />
                  {attachment.name}
                </span>
              ))}
            </div>
          )}

          <ChatComposer value={prompt} onChange={setPrompt} onSubmit={sendMessage} disabled={busy} />
        </div>
      </section>

      <aside className="apoema-panel apoema-chat-right">
        <div className="apoema-section-head">
          <h2>Boas práticas</h2>
          <span>Guard rails</span>
        </div>
        <div className="apoema-safety-list">
          <div className="apoema-safety-item">
            <ShieldAlert size={16} />
            <div>
              <strong>Sem segredos</strong>
              <p>.env, tokens e bases locais são sinalizados antes do envio.</p>
            </div>
          </div>
          <div className="apoema-safety-item">
            <Sparkles size={16} />
            <div>
              <strong>Respostas concisas</strong>
              <p>O assistente prioriza contexto operacional e ações sugeridas.</p>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}
