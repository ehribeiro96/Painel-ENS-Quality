import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Paperclip, ShieldAlert, Sparkles } from "lucide-react";
import { ChatComposer } from "../components/ChatComposer";
import { ChatMessage } from "../components/ChatMessage";
import { FileDropzone } from "../components/FileDropzone";
import { StatusPill } from "../components/StatusPill";
import { apoemaConversations, apoemaInitialMessages } from "../data";
import { attachmentWarning } from "../mockApi";
import { getAiProviders, sendAiMessage } from "../lib/apoemaChatApi";
import { useAuth } from "@/lib/auth";
import type {
  ApoemaAttachment,
  ApoemaChatAttachmentMeta,
  ApoemaChatStatus,
  ApoemaMessage,
  ApoemaProviderOption,
} from "../types";

function humanSize(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  const kb = bytes / 1024;
  return `${kb.toFixed(kb >= 10 ? 0 : 1)} KB`;
}

function classifyAttachmentKind(file: File): ApoemaChatAttachmentMeta["kind"] {
  const lowerName = file.name.toLowerCase();
  if (file.type.startsWith("image/")) return "image";
  if (file.type === "application/pdf" || lowerName.endsWith(".pdf")) return "pdf";
  if (file.type.includes("spreadsheet") || /\.(csv|xls|xlsx|ods|tsv)$/i.test(lowerName)) return "spreadsheet";
  if (/\.(ts|tsx|js|jsx|py|sh|ps1|bat|cmd)$/i.test(lowerName)) return "script";
  if (lowerName.endsWith(".log")) return "log";
  if (file.type.startsWith("text/") || /\.(txt|md|json|yaml|yml|xml|sql|ini)$/i.test(lowerName)) return "text";
  return "unknown";
}

function toAttachment(file: File): ApoemaAttachment {
  return {
    id: `${file.name}-${file.size}-${file.lastModified}`,
    name: file.name,
    size: humanSize(file.size),
    sizeBytes: file.size,
    mimeType: file.type || "application/octet-stream",
    kind: classifyAttachmentKind(file),
    sensitive: /\.(env|pem|key|sqlite|db|sql)$/i.test(file.name),
  };
}

function formatClock(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function statusTone(status?: ApoemaProviderOption["status"]) {
  switch (status) {
    case "online":
      return "success";
    case "offline":
    case "error":
      return "warning";
    case "unconfigured":
      return "info";
    default:
      return "neutral";
  }
}

const FALLBACK_PROVIDER: ApoemaProviderOption = {
  id: "mock",
  label: "Mock/Fallback",
  status: "online",
  models: ["fallback-local"],
  default_model: "fallback-local",
};

export function ChatPage() {
  const { token } = useAuth();
  const [conversationId, setConversationId] = useState(apoemaConversations[0]?.id ?? "");
  const [messages, setMessages] = useState<ApoemaMessage[]>(apoemaInitialMessages);
  const [prompt, setPrompt] = useState("");
  const [attachments, setAttachments] = useState<ApoemaAttachment[]>([]);
  const [busy, setBusy] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [providers, setProviders] = useState<ApoemaProviderOption[]>([FALLBACK_PROVIDER]);
  const [selectedProviderId, setSelectedProviderId] = useState("mock");
  const [selectedModel, setSelectedModel] = useState(FALLBACK_PROVIDER.default_model);
  const [notice, setNotice] = useState<string | null>(null);
  const [providerLoadStatus, setProviderLoadStatus] = useState<ApoemaChatStatus>("ok");

  const warning = useMemo(() => attachmentWarning(attachments), [attachments]);
  const selectedProvider = useMemo(
    () => providers.find((provider) => provider.id === selectedProviderId) ?? providers[0] ?? FALLBACK_PROVIDER,
    [providers, selectedProviderId],
  );
  const providerModels = useMemo(() => {
    const models = selectedProvider.models.length > 0 ? selectedProvider.models : [selectedProvider.default_model];
    return Array.from(new Set([selectedProvider.default_model, ...models]));
  }, [selectedProvider]);

  useEffect(() => {
    let active = true;
    getAiProviders(token)
      .then((items) => {
        if (!active) return;
        setProviders(items.length > 0 ? items : [FALLBACK_PROVIDER]);
        const firstProvider = items[0] ?? FALLBACK_PROVIDER;
        setSelectedProviderId((current) => items.some((provider) => provider.id === current) ? current : firstProvider.id);
        setSelectedModel((current) => (firstProvider.models.includes(current) ? current : firstProvider.default_model));
        setProviderLoadStatus("ok");
      })
      .catch(() => {
        if (!active) return;
        setProviders([FALLBACK_PROVIDER]);
        setSelectedProviderId("mock");
        setSelectedModel(FALLBACK_PROVIDER.default_model);
        setProviderLoadStatus("offline");
        setNotice("Usando fallback local para manter a conversa ativa.");
      });
    return () => {
      active = false;
    };
  }, [token]);

  useEffect(() => {
    if (!providerModels.includes(selectedModel)) {
      setSelectedModel(selectedProvider.default_model);
    }
  }, [providerModels, selectedModel, selectedProvider.default_model]);

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
      attachments,
    };

    setMessages((current) => [...current, userMessage]);
    setPrompt("");
    setBusy(true);
    setNotice(null);

    try {
      const response = await sendAiMessage({
        conversation_id: conversationId || null,
        provider: selectedProvider.id,
        model: selectedModel || selectedProvider.default_model,
        message: content,
        mode: "assistente_n2",
        attachments: attachments.map((attachment) => ({
          id: attachment.id,
          name: attachment.name,
          mime_type: attachment.mimeType,
          size: attachment.sizeBytes,
          kind: attachment.kind,
          sensitive: Boolean(attachment.sensitive),
        })),
        context: {
          route: "apoema-chat",
          source: "apoema-preview",
        },
      }, token);

      setConversationId(response.conversation_id);
      setMessages((current) => [
        ...current,
        {
          id: response.message_id,
          role: "assistant",
          content: response.content,
          time: formatClock(response.created_at),
        },
      ]);
      if (response.status !== "ok") {
        setNotice(
          response.status === "unconfigured"
            ? "O provedor Hermes está sem configuração. Usando fallback local para manter a conversa ativa."
            : "O provedor de IA está offline. Verifique a configuração do Ollama ou Hermes.",
        );
      }
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: `assistant-fallback-${Date.now()}`,
          role: "assistant",
          content: "Não foi possível enviar a mensagem. Usando fallback local para manter a conversa ativa.",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
      setNotice("Usando fallback local para manter a conversa ativa.");
    } finally {
      setAttachments([]);
      setBusy(false);
    }
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
          <p>{"Frontend Apoema -> Backend do Painel -> Provedor controlado no servidor."}</p>
        </div>
      </aside>

      <section className="apoema-panel apoema-chat-main">
        <div className="apoema-section-head">
          <div>
            <StatusPill tone="info">Assistente Apoema</StatusPill>
            <h1>Como posso ajudar?</h1>
          </div>
          <div style={{ display: "grid", gap: 10, minWidth: 320 }}>
            <label className="apoema-provider-select">
              Provedor
              <select
                value={selectedProviderId}
                onChange={(event) => {
                  const nextProvider = providers.find((provider) => provider.id === event.target.value) ?? FALLBACK_PROVIDER;
                  setSelectedProviderId(nextProvider.id);
                  setSelectedModel(nextProvider.default_model);
                  setNotice(null);
                }}
              >
                {providers.map((provider) => (
                  <option key={provider.id} value={provider.id}>
                    {provider.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="apoema-provider-select">
              Modelo
              <select
                value={selectedModel}
                onChange={(event) => {
                  setSelectedModel(event.target.value);
                  setNotice(null);
                }}
              >
                {providerModels.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <div className="apoema-chat-messages" aria-live="polite">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
        </div>

        <div className="apoema-chat-dock">
          {notice && (
            <div className="apoema-warning">
              <AlertTriangle size={16} />
              <div>
                <strong>Fallback ativo</strong>
                <p>{notice}</p>
              </div>
            </div>
          )}

          <FileDropzone
            dragging={dragging}
            onDragStateChange={setDragging}
            onFiles={addFiles}
            label="Arraste e solte arquivos para anexar ao contexto"
          />

          {warning && (
            <div className="apoema-warning">
              <ShieldAlert size={16} />
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
          <div className="apoema-chat-sidebar-card" aria-live="polite">
            <StatusPill tone={statusTone(selectedProvider.status)}>
              {providerLoadStatus === "offline" ? "Fallback local" : selectedProvider.status}
            </StatusPill>
            <p>
              Modelo atual: <strong>{selectedModel}</strong>. A conversa usa metadados de anexos e mantém o fluxo visual local.
            </p>
          </div>
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
