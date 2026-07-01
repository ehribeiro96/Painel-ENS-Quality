import { AlertTriangle, RotateCcw, ShieldAlert, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ChatComposer } from "../components/ChatComposer";
import { ChatConversationSidebar } from "../components/ChatConversationSidebar";
import { ChatMessage } from "../components/ChatMessage";
import { StatusPill } from "../components/StatusPill";
import { useAuth } from "@/lib/auth";
import {
  createAiChatConversation,
  getAiChatConversation,
  getAiChatProviders,
  listAiChatConversations,
  sendAiChatConversationMessage,
} from "../lib/apoemaChatBridgeApi";
import { AiChatApiError } from "../types";
import type { AiChatConversation, AiChatProvider, ApoemaProviderLoadState } from "../types";

type ChatBannerTone = "warning" | "danger";

type ChatBanner = {
  tone: ChatBannerTone;
  title: string;
  message: string;
};

type ConversationLoadState = "loading" | "ready" | "fallback" | "error";

const CHAT_MODE = "general";

function formatClock(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function statusTone(status?: AiChatProvider["status"]) {
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

function chooseConversationId(conversations: AiChatConversation[], preferredId?: string | null) {
  if (preferredId && conversations.some((conversation) => conversation.id === preferredId)) {
    return preferredId;
  }
  return conversations[0]?.id ?? "";
}

function summarizeConversation(conversation: AiChatConversation): AiChatConversation {
  const { messages: _messages, ...summary } = conversation;
  return {
    ...summary,
    metadata: { ...summary.metadata },
  };
}

function describeAiChatApiError(error: unknown): ChatBanner {
  if (error instanceof AiChatApiError) {
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
      case "not_found":
        return {
          tone: "warning",
          title: "Conversa não encontrada",
          message: "A conversa solicitada não foi encontrada.",
        };
      case "expired":
        return {
          tone: "warning",
          title: "Recurso expirado",
          message: "O recurso solicitado expirou. Recarregue a conversa.",
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
  const [providers, setProviders] = useState<AiChatProvider[]>([]);
  const [selectedProviderId, setSelectedProviderId] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [providerLoadState, setProviderLoadState] = useState<ApoemaProviderLoadState>("loading");
  const [providerBanner, setProviderBanner] = useState<ChatBanner | null>(null);

  const [conversations, setConversations] = useState<AiChatConversation[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState("");
  const [conversationDetail, setConversationDetail] = useState<AiChatConversation | null>(null);
  const [conversationLoadState, setConversationLoadState] = useState<ConversationLoadState>("loading");
  const [conversationBanner, setConversationBanner] = useState<ChatBanner | null>(null);

  const [prompt, setPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [creatingConversation, setCreatingConversation] = useState(false);
  const [messageBanner, setMessageBanner] = useState<ChatBanner | null>(null);

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
  const visibleMessages = conversationDetail?.messages ?? [];

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

  async function reloadProviders() {
    setProviderLoadState("loading");
    setProviderBanner(null);

    try {
      const result = await getAiChatProviders(token);
      if (result.kind === "fallback") {
        const firstProvider = result.providers[0] ?? null;
        setProviders(result.providers);
        setSelectedProviderId(firstProvider?.id ?? "");
        setSelectedModel(firstProvider?.default_model ?? "");
        setProviderLoadState("fallback");
        setProviderBanner({
          tone: "warning",
          title: "Fallback local ativo",
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
    } catch (error) {
      setProviders([]);
      setSelectedProviderId("");
      setSelectedModel("");
      setProviderLoadState("error");
      setProviderBanner(describeAiChatApiError(error));
    }
  }

  async function reloadConversations(preferredConversationId?: string | null) {
    setConversationLoadState("loading");
    setConversationBanner(null);

    try {
      const result = await listAiChatConversations(token);
      const nextConversations = result.conversations.map((conversation) => summarizeConversation(conversation));
      setConversations(nextConversations);

      const nextConversationId = chooseConversationId(nextConversations, preferredConversationId ?? selectedConversationId);
      setSelectedConversationId(nextConversationId);
      if (nextConversationId) {
        await loadConversationDetail(nextConversationId);
      } else {
        setConversationDetail(null);
        setConversationLoadState(result.kind === "fallback" ? "fallback" : "ready");
      }

      if (result.kind === "fallback") {
        setConversationBanner({
          tone: "warning",
          title: "Fallback local ativo",
          message: result.notice,
        });
      }
    } catch (error) {
      setConversations([]);
      setSelectedConversationId("");
      setConversationDetail(null);
      setConversationLoadState("error");
      setConversationBanner(describeAiChatApiError(error));
    }
  }

  async function loadConversationDetail(conversationId: string) {
    if (!conversationId) {
      setConversationDetail(null);
      return;
    }

    setConversationLoadState("loading");
    setConversationDetail(null);

    try {
      const result = await getAiChatConversation(conversationId, token);
      if (!result) {
        setConversationDetail(null);
        setConversationLoadState("error");
        setConversationBanner({
          tone: "warning",
          title: "Conversa indisponível",
          message: "A conversa selecionada não está disponível neste momento.",
        });
        return;
      }

      setConversationDetail(result.conversation);
      if (result.kind === "fallback") {
        setConversationLoadState("fallback");
        setConversationBanner({
          tone: "warning",
          title: "Fallback local ativo",
          message: result.notice,
        });
      } else {
        setConversationLoadState("ready");
        setConversationBanner(null);
      }
    } catch (error) {
      setConversationDetail(null);
      setConversationLoadState("error");
      setConversationBanner(describeAiChatApiError(error));
    }
  }

  useEffect(() => {
    void reloadProviders();
    void reloadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    if (selectedProvider && !providerModels.includes(selectedModel)) {
      setSelectedModel(selectedProvider.default_model);
    }
  }, [providerModels, selectedModel, selectedProvider]);

  async function handleNewConversation() {
    if (creatingConversation) {
      return;
    }

    setCreatingConversation(true);
    setMessageBanner(null);

    try {
      const result = await createAiChatConversation(
        {
          title: "Nova conversa",
          mode: CHAT_MODE,
        },
        token,
      );

      setConversations((current) => {
        const next = [summarizeConversation(result.conversation), ...current.filter((conversation) => conversation.id !== result.conversation.id)];
        return next;
      });
      setSelectedConversationId(result.conversation.id);
      setConversationDetail(result.conversation);
      setConversationLoadState(result.kind === "fallback" ? "fallback" : "ready");
      if (result.kind === "fallback") {
        setConversationBanner({
          tone: "warning",
          title: "Fallback local ativo",
          message: result.notice,
        });
      } else {
        setConversationBanner(null);
      }
    } catch (error) {
      setMessageBanner(describeAiChatApiError(error));
    } finally {
      setCreatingConversation(false);
    }
  }

  async function sendMessage() {
    if (busy || !providerReady || !selectedProvider) {
      return;
    }

    const content = prompt.trim();
    if (!content) {
      setMessageBanner({
        tone: "warning",
        title: "Mensagem vazia",
        message: "Digite uma mensagem para enviar ao backend.",
      });
      return;
    }

    setBusy(true);
    setMessageBanner(null);

    try {
      if (!selectedConversationId) {
        const result = await createAiChatConversation(
          {
            title: content.length > 54 ? `${content.slice(0, 51).trimEnd()}...` : content,
            message: content,
            mode: CHAT_MODE,
          },
          token,
        );
        setConversations((current) => {
          const next = [summarizeConversation(result.conversation), ...current.filter((conversation) => conversation.id !== result.conversation.id)];
          return next;
        });
        setSelectedConversationId(result.conversation.id);
        setConversationDetail(result.conversation);
        setConversationLoadState(result.kind === "fallback" ? "fallback" : "ready");
        if (result.kind === "fallback") {
          setConversationBanner({
            tone: "warning",
            title: "Fallback local ativo",
            message: result.notice,
          });
        } else {
          setConversationBanner(null);
        }
      } else {
        const result = await sendAiChatConversationMessage(
          selectedConversationId,
          {
            content,
            mode: CHAT_MODE,
          },
          token,
        );
        setConversations((current) => {
          const next = [summarizeConversation(result.conversation), ...current.filter((conversation) => conversation.id !== result.conversation.id)];
          return next;
        });
        setConversationDetail(result.conversation);
        setConversationLoadState(result.kind === "fallback" ? "fallback" : "ready");
        if (result.kind === "fallback") {
          setConversationBanner({
            tone: "warning",
            title: "Fallback local ativo",
            message: result.notice,
          });
        } else {
          setConversationBanner(null);
        }
      }

      setPrompt("");
    } catch (error) {
      setMessageBanner(describeAiChatApiError(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="apoema-chat-layout">
      {/* Conversas backend-backed */}
      <ChatConversationSidebar
        conversations={conversations}
        selectedConversationId={selectedConversationId || null}
        loading={conversationLoadState === "loading" || (Boolean(selectedConversationId) && !conversationDetail)}
        state={conversationLoadState}
        banner={conversationBanner}
        fallbackNotice={conversationLoadState === "fallback" ? conversationBanner?.message ?? null : null}
        onSelectConversation={(conversationId) => {
          setSelectedConversationId(conversationId);
          void loadConversationDetail(conversationId);
          setMessageBanner(null);
        }}
        onNewConversation={() => void handleNewConversation()}
        onReload={() => void reloadConversations(selectedConversationId || null)}
        creatingConversation={creatingConversation}
      />

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
                    <button type="button" className="apoema-secondary-button" onClick={() => void reloadProviders()} disabled={providerLoadState === "loading"}>
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
          {selectedConversationId && conversationLoadState === "loading" && conversationDetail === null ? (
            <div className="apoema-chat-empty-state">
              <strong>Carregando conversa...</strong>
              <p>Buscando o histórico selecionado no backend.</p>
            </div>
          ) : selectedConversationId && visibleMessages.length > 0 ? (
            visibleMessages.map((message) => <ChatMessage key={message.id} message={message} />)
          ) : (
            <div className="apoema-chat-empty-state">
              <strong>Sem mensagens ainda</strong>
              <p>Crie uma conversa nova ou envie a primeira mensagem para iniciar o histórico do backend.</p>
            </div>
          )}
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

          <ChatComposer
            value={prompt}
            onChange={setPrompt}
            onSubmit={sendMessage}
            disabled={!providerReady || !selectedProvider}
            isSending={busy}
          />

          <div className="apoema-chat-sidebar-card" aria-live="polite">
            <StatusPill tone={providerStateTone as "success" | "warning" | "neutral" | "info"}>
              {providerStateLabel}
            </StatusPill>
            <p>
              {selectedProvider?.id === "mock"
                ? "Frontend Apoema → Backend do Painel → adaptador mock local determinístico para UAT."
                : "Frontend Apoema → Backend do Painel → provedor controlado no servidor."}
            </p>
          </div>

          <div className="apoema-chat-sidebar-card">
            <StatusPill tone="warning">
              <ShieldAlert size={14} />
              Proteções
            </StatusPill>
            <p>Sem segredos, sem respostas progressivas inventadas e sem anexos backend-backed nesta fase.</p>
          </div>
        </div>
      </section>

      <aside className="apoema-chat-right apoema-panel">
        <div className="apoema-chat-sidebar-card">
          <StatusPill tone="success">
            <Sparkles size={14} />
            Sem segredos
          </StatusPill>
          <p>O chat conversa com o backend do Painel e não expõe tokens, provider keys ou paths internos.</p>
        </div>
        <div className="apoema-chat-sidebar-card">
          <StatusPill tone="info">Operação</StatusPill>
          <p>Histórico backend-backed, mensagens em PT-BR e fallback local apenas quando a rede falha.</p>
        </div>
        <div className="apoema-chat-sidebar-card">
          <StatusPill tone="neutral">Tempo</StatusPill>
          <p>{conversationDetail?.updated_at ? `Última atualização: ${formatClock(conversationDetail.updated_at)}` : "Nenhuma conversa selecionada."}</p>
        </div>
      </aside>
    </div>
  );
}
