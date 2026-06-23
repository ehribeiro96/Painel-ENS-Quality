import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Paperclip, RotateCcw, ShieldAlert, Sparkles } from "lucide-react";
import { ChatComposer } from "../components/ChatComposer";
import { ChatMessage } from "../components/ChatMessage";
import { FileDropzone } from "../components/FileDropzone";
import { StatusPill } from "../components/StatusPill";
import { apoemaConversations, apoemaInitialMessages } from "../data";
import { attachmentWarning } from "../mockApi";
import { getAiProviders, sendAiMessage } from "../lib/apoemaChatApi";
import { useAuth } from "@/lib/auth";
import { ApoemaApiError } from "../types";
import type {
  ApoemaAttachment,
  ApoemaChatAttachmentMeta,
  ApoemaMessage,
  ApoemaProviderLoadState,
  ApoemaProviderOption,
} from "../types";

type ApoemaBannerTone = "warning" | "danger";

type ApoemaBanner = {
  tone: ApoemaBannerTone;
  title: string;
  message: string;
};

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

function describeApoemaApiError(error: unknown): ApoemaBanner {
  if (error instanceof ApoemaApiError) {
    switch (error.kind) {
      case "auth_required":
        return {
          tone: "danger",
          title: "Sessão expirada",
          message: "Sua sessão expirou ou não foi autenticada. Faça login novamente para usar o Chat de IA.",
        };
      case "forbidden":
        return {
          tone: "danger",
          title: "Sem permissão",
          message: "Você não tem permissão para usar este recurso.",
        };
      case "rate_limited":
        return {
          tone: "warning",
          title: "Limite atingido",
          message: "Limite de uso atingido. Aguarde alguns instantes e tente novamente.",
        };
      case "validation_error":
        return {
          tone: "warning",
          title: "Requisição inválida",
          message: "A requisição de IA é inválida. Revise os campos e tente novamente.",
        };
      case "backend_error":
        return {
          tone: "danger",
          title: "Erro do backend",
          message: "O backend de IA retornou um erro. Tente novamente em instantes.",
        };
      case "network_unavailable":
        return {
          tone: "warning",
          title: "Fallback local ativo",
          message: "Backend indisponível. Exibindo resposta local de fallback.",
        };
      default:
        return {
          tone: "danger",
          title: "Erro da API",
          message: "A API de IA retornou uma resposta inesperada.",
        };
    }
  }

  return {
    tone: "danger",
    title: "Erro inesperado",
    message: "Não foi possível concluir a operação. Tente novamente em instantes.",
  };
}

export function ChatPage() {
  const { token } = useAuth();
  const [conversationId, setConversationId] = useState(apoemaConversations[0]?.id ?? "");
  const [messages, setMessages] = useState<ApoemaMessage[]>(apoemaInitialMessages);
  const [prompt, setPrompt] = useState("");
  const [attachments, setAttachments] = useState<ApoemaAttachment[]>([]);
  const [busy, setBusy] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [providers, setProviders] = useState<ApoemaProviderOption[]>([]);
  const [selectedProviderId, setSelectedProviderId] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [providerLoadState, setProviderLoadState] = useState<ApoemaProviderLoadState>("loading");
  const [providerBanner, setProviderBanner] = useState<ApoemaBanner | null>(null);
  const [messageBanner, setMessageBanner] = useState<ApoemaBanner | null>(null);

  const warning = useMemo(() => attachmentWarning(attachments), [attachments]);
  const selectedProvider = useMemo(
    () => providers.find((provider) => provider.id === selectedProviderId) ?? null,
    [providers, selectedProviderId],
  );
  const providerModels = useMemo(() => {
    if (!selectedProvider) {
      return [];
    }
    const models = selectedProvider.models.length > 0 ? selectedProvider.models : [selectedProvider.default_model];
    return Array.from(new Set([selectedProvider.default_model, ...models]));
  }, [selectedProvider]);
  const providerReady = providerLoadState === "ready" || providerLoadState === "fallback";

  async function reloadProviders(guard: () => boolean = () => true) {
    setProviderLoadState("loading");
    setProviderBanner(null);

    try {
      const result = await getAiProviders(token);
      if (!guard()) {
        return;
      }

      if (result.kind === "fallback") {
        const firstProvider = result.providers[0] ?? null;
        setProviders(result.providers);
        setSelectedProviderId(firstProvider?.id ?? "");
        setSelectedModel(firstProvider?.default_model ?? "");
        setProviderLoadState("fallback");
        setProviderBanner({
          tone: "warning",
          title: "Backend indisponível",
          message: result.notice,
        });
        return;
      }

      if (result.providers.length === 0) {
        setProviders([]);
        setSelectedProviderId("");
        setSelectedModel("");
        setProviderLoadState("error");
        setProviderBanner({
          tone: "danger",
          title: "Catálogo indisponível",
          message: "O backend não retornou provedores disponíveis.",
        });
        return;
      }

      const firstProvider = result.providers[0];
      setProviders(result.providers);
      setSelectedProviderId(firstProvider.id);
      setSelectedModel(firstProvider.default_model);
      setProviderLoadState("ready");
      setProviderBanner(null);
    } catch (error) {
      if (!guard()) {
        return;
      }
      const banner = describeApoemaApiError(error);
      setProviders([]);
      setSelectedProviderId("");
      setSelectedModel("");
      setProviderLoadState("error");
      setProviderBanner(banner);
    }
  }

  useEffect(() => {
    let active = true;
    void reloadProviders(() => active);
    return () => {
      active = false;
    };
  }, [token]);

  useEffect(() => {
    if (selectedProvider && !providerModels.includes(selectedModel)) {
      setSelectedModel(selectedProvider.default_model);
    }
  }, [providerModels, selectedModel, selectedProvider]);

  async function sendMessage() {
    if (busy || !providerReady || !selectedProvider) {
      return;
    }

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
    setMessageBanner(null);

    try {
      const result = await sendAiMessage(
        {
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
        },
        token,
      );

      if (result.kind === "fallback") {
        setConversationId(result.response.conversation_id);
        setMessages((current) => [
          ...current,
          {
            id: result.response.message_id,
            role: "assistant",
            content: result.response.content,
            time: formatClock(result.response.created_at),
            source: "fallback",
          },
        ]);
        setMessageBanner({
          tone: "warning",
          title: "Fallback local ativo",
          message: result.notice,
        });
        return;
      }

      const response = result.response;
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
        setMessageBanner({
          tone: response.status === "unconfigured" ? "warning" : "warning",
          title: response.status === "unconfigured" ? "Provedor sem configuração" : "Provedor de IA indisponível",
          message:
            response.status === "unconfigured"
              ? "O provedor Hermes está sem configuração. A resposta veio do backend em modo degradado."
              : "O provedor de IA está offline. Verifique a configuração do Ollama ou Hermes.",
        });
      }
    } catch (error) {
      setMessageBanner(describeApoemaApiError(error));
    } finally {
      setAttachments([]);
      setBusy(false);
    }
  }

  function addFiles(files: File[]) {
    const mapped = files.map(toAttachment);
    setAttachments((current) => [...current, ...mapped]);
  }

  const providerStateTone =
    providerLoadState === "loading"
      ? "neutral"
      : providerLoadState === "fallback" || providerLoadState === "error"
        ? "warning"
        : statusTone(selectedProvider?.status);

  const providerStateLabel =
    providerLoadState === "loading"
      ? "Carregando provedores"
      : providerLoadState === "fallback"
        ? "Fallback local"
        : providerLoadState === "error"
          ? "Catálogo indisponível"
          : selectedProvider?.status ?? "Sem provedor";

  return (
    <div className="apoema-chat-layout">
      <aside className="apoema-chat-sidebar apoema-panel">
        <div className="apoema-section-head">
          <h2>Conversas</h2>
          <span>Painel</span>
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
          <p>{"Frontend Apoema → Backend do Painel → provedor controlado no servidor."}</p>
        </div>
      </aside>

      <section className="apoema-panel apoema-chat-main">
        <div className="apoema-section-head">
          <div>
            <StatusPill tone="info">Assistente Apoema</StatusPill>
            <h1>Como posso ajudar?</h1>
          </div>
          <div style={{ display: "grid", gap: 10, minWidth: 320 }}>
            {providerLoadState === "loading" && (
              <div className="apoema-warning is-warning">
                <AlertTriangle size={16} />
                <div>
                  <strong>Carregando provedores</strong>
                  <p>Buscando catálogo do backend de IA.</p>
                </div>
              </div>
            )}

            {providerBanner && (
              <div className={`apoema-warning ${providerBanner.tone === "danger" ? "is-danger" : "is-warning"}`}>
                {providerBanner.tone === "danger" ? <ShieldAlert size={16} /> : <AlertTriangle size={16} />}
                <div>
                  <strong>{providerBanner.title}</strong>
                  <p>{providerBanner.message}</p>
                  <div className="apoema-warning-actions">
                    <button type="button" className="apoema-secondary-button" onClick={() => void reloadProviders()}>
                      <RotateCcw size={16} />
                      Tentar novamente
                    </button>
                  </div>
                </div>
              </div>
            )}

            {providerReady && selectedProvider && (
              <>
                <label className="apoema-provider-select">
                  Provedor
                  <select
                    value={selectedProviderId}
                    onChange={(event) => {
                      const nextProvider = providers.find((provider) => provider.id === event.target.value);
                      if (!nextProvider) {
                        return;
                      }
                      setSelectedProviderId(nextProvider.id);
                      setSelectedModel(nextProvider.default_model);
                      setMessageBanner(null);
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
                      setMessageBanner(null);
                    }}
                  >
                    {providerModels.map((model) => (
                      <option key={model} value={model}>
                        {model}
                      </option>
                    ))}
                  </select>
                </label>
              </>
            )}
          </div>
        </div>

        <div className="apoema-chat-messages" aria-live="polite">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
        </div>

        <div className="apoema-chat-dock">
          {messageBanner && (
            <div className={`apoema-warning ${messageBanner.tone === "danger" ? "is-danger" : "is-warning"}`}>
              {messageBanner.tone === "danger" ? <ShieldAlert size={16} /> : <AlertTriangle size={16} />}
              <div>
                <strong>{messageBanner.title}</strong>
                <p>{messageBanner.message}</p>
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
            <div className="apoema-warning is-warning">
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

          <ChatComposer
            value={prompt}
            onChange={setPrompt}
            onSubmit={sendMessage}
            disabled={busy || !providerReady || !selectedProvider}
          />
          <div className="apoema-chat-sidebar-card" aria-live="polite">
            <StatusPill tone={providerStateTone as "success" | "warning" | "neutral" | "info"}>
              {providerStateLabel}
            </StatusPill>
            <p>
              {providerLoadState === "fallback"
                ? "Backend indisponível. Catálogo local ativo para continuidade da prévia."
                : providerLoadState === "error"
                  ? "O catálogo de provedores não pôde ser carregado."
                  : selectedProvider
                    ? `Modelo atual: ${selectedModel || selectedProvider.default_model}. A conversa usa metadados de anexos e mantém o fluxo visual local.`
                    : "Aguardando catálogo de provedores."}
            </p>
          </div>
        </div>
      </section>

      <aside className="apoema-panel apoema-chat-right">
        <div className="apoema-section-head">
          <h2>Boas práticas</h2>
          <span>Proteções</span>
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
