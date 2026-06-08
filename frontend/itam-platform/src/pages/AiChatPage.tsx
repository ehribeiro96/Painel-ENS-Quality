import { useEffect, useState } from "react";
import { ChatComposer } from "@/components/ai-chat/ChatComposer";
import { ChatMessages } from "@/components/ai-chat/ChatMessages";
import { ConversationList } from "@/components/ai-chat/ConversationList";
import { PromptPresets } from "@/components/ai-chat/PromptPresets";
import { ApiError, api, mapAiChatError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { AiChatConversation, AiChatConversationDetail, AiChatMode, AiChatProviderHealth } from "@/lib/types";

type AiChatErrorState = {
  error: ApiError;
  context?: string;
};

function toApiError(error: unknown, fallbackMessage: string) {
  return error instanceof ApiError ? error : new ApiError(fallbackMessage, 0, null);
}

export function AiChatPage() {
  const { token } = useAuth();
  const [conversations, setConversations] = useState<AiChatConversation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<AiChatConversationDetail | null>(null);
  const [composer, setComposer] = useState("");
  const [selectedMode, setSelectedMode] = useState<AiChatMode>("general");
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [errorState, setErrorState] = useState<AiChatErrorState | null>(null);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);
  const [providerHealth, setProviderHealth] = useState<AiChatProviderHealth | null>(null);

  async function refreshConversations(nextSelectedId?: string | null, shouldClearComposer = true) {
    if (!token) {
      return;
    }
    const items = await api.aiChatConversations(token);
    setConversations(items);
    const targetId = nextSelectedId ?? selectedId ?? items[0]?.id ?? null;
    setSelectedId(targetId);
    if (targetId) {
      setDetail(await api.aiChatConversation(token, targetId));
    } else {
      setDetail(null);
    }
    if (shouldClearComposer) {
      setComposer("");
    }
  }

  useEffect(() => {
    if (!token) {
      setProviderHealth(null);
      return;
    }
    api.aiChatHealth(token)
      .then(setProviderHealth)
      .catch((err: unknown) => {
        setErrorState({ error: toApiError(err, "Erro desconhecido ao verificar saúde do AI Chat.") });
        setProviderHealth(null);
      });
  }, [token]);

  useEffect(() => {
    if (!token) {
      return;
    }
    setLoading(true);
    refreshConversations(undefined, false)
      .catch((err: unknown) => setErrorState({ error: toApiError(err, "Erro desconhecido ao carregar conversas.") }))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function createConversation() {
    if (!token || loading || sending) {
      return;
    }
    setLoading(true);
    setErrorState(null);
    try {
      const conversation = await api.aiChatCreateConversation(token, { title: "Nova conversa" });
      setDetail(conversation);
      await refreshConversations(conversation.id, false);
    } catch (err: unknown) {
      setErrorState({ error: toApiError(err, "Erro desconhecido ao criar conversa.") });
    } finally {
      setLoading(false);
    }
  }

  async function selectConversation(id: string) {
    if (!token || sending) {
      return;
    }
    setSelectedId(id);
    setLoading(true);
    setErrorState(null);
    try {
      setDetail(await api.aiChatConversation(token, id));
      setComposer("");
    } catch (err: unknown) {
      setErrorState({ error: toApiError(err, "Erro desconhecido ao abrir conversa.") });
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage(content: string) {
    if (!token || !providerHealth?.enabled || loading || sending) {
      return;
    }

    setSending(true);
    setErrorState(null);
    let conversationId = selectedId;
    let conversationCreated = false;

    try {
      if (!conversationId) {
        const conversation = await api.aiChatCreateConversation(token, { title: content.slice(0, 80) || "Nova conversa" });
        conversationId = conversation.id;
        conversationCreated = true;
        setSelectedId(conversationId);
        setDetail(conversation);
        await refreshConversations(conversationId, false);
      } else {
        setDetail((prev) => prev ? ({
          ...prev,
          messages: [
            ...prev.messages,
            {
              id: `temp-${Date.now()}`,
              conversation_id: prev.id,
              role: "user",
              content,
              created_at: new Date().toISOString(),
              provider: null,
              model: null,
            }
          ]
        }) : prev);
      }

      const nextDetail = await api.aiChatSendMessage(token, conversationId, content, selectedMode);
      setDetail(nextDetail);
      await refreshConversations(conversationId, true);
    } catch (err: unknown) {
      const context = conversationCreated
        ? "A conversa foi criada, mas o envio da mensagem falhou. O texto foi mantido para você tentar novamente."
        : "O envio da mensagem falhou. O texto foi mantido para você tentar novamente.";
      setErrorState({ error: toApiError(err, "Erro desconhecido ao enviar mensagem."), context });
      if (conversationId) {
        await refreshConversations(conversationId, false).catch(() => undefined);
      }
    } finally {
      setSending(false);
    }
  }

  async function copyResponse(content: string) {
    await navigator.clipboard.writeText(content);
    setCopyStatus("Resposta copiada.");
    window.setTimeout(() => setCopyStatus(null), 2000);
  }

  const mappedError = errorState ? mapAiChatError(errorState.error) : null;
  const isChatDisabled = providerHealth ? !providerHealth.enabled : false;
  const composerDisabled = loading || sending || isChatDisabled;
  const providerLabel = providerHealth
    ? `${providerHealth.provider}${providerHealth.model ? ` (${providerHealth.model})` : ""}`
    : null;
  const modeLabels: Record<AiChatMode, string> = {
    general: "Geral",
    fix_text: "Corrigir texto",
    draft_ticket: "Abertura ITIL",
    update_ticket: "Atualização",
    resolution: "Solução aplicada",
    summarize: "Resumir",
    improve_tone: "Melhorar tom",
    service_macro: "Macro",
    asset_guidance: "Orientação de ativo"
  };

  function applyPreset(preset: { mode: AiChatMode; text: string }) {
    setSelectedMode(preset.mode);
    setComposer((current) => current.startsWith(preset.text) ? current : `${preset.text}${current}`);
  }

  return (
    <div className="ai-chat-page">
      <div className="page-title">
        <div>
          <h1>IA Chat</h1>
          <p>A IA não executa ações no sistema. Use apenas para apoio textual.</p>
          {providerLabel && (
            <span className="ai-chat-provider-badge" title={`Provider ${providerLabel} - Status: ${providerHealth?.status ?? "indisponível"}`}>
              {providerLabel}
            </span>
          )}
          <span className="ai-chat-mode-badge" title="Modo textual selecionado">
            Modo: {modeLabels[selectedMode]}
          </span>
        </div>
      </div>

      {isChatDisabled && (
        <div className="alert warning">
          <strong>IA Chat desabilitado</strong>
          <p>O módulo AI Chat está desabilitado no backend. Habilite ENABLE_AI_CHAT=true no runtime do app.</p>
          {providerHealth?.detail && (
            <details>
              <summary>Detalhes técnicos</summary>
              <pre>{providerHealth.detail}</pre>
            </details>
          )}
        </div>
      )}

      {mappedError && (
        <div className={`alert ${mappedError.severity}`}>
          <strong>{mappedError.title}</strong>
          {errorState?.context ? <p>{errorState.context}</p> : null}
          <p>{mappedError.message}</p>
          {mappedError.technical && (
            <details>
              <summary>Detalhes técnicos</summary>
              <pre>{mappedError.technical}</pre>
            </details>
          )}
        </div>
      )}

      {copyStatus ? <div className="alert success">{copyStatus}</div> : null}

      <div className="ai-chat-grid">
        <ConversationList
          conversations={conversations}
          selectedId={selectedId}
          loading={loading || sending}
          onSelect={(id) => void selectConversation(id)}
          onNewConversation={() => void createConversation()}
        />
        <section className="ai-chat-main card">
          <PromptPresets selectedMode={selectedMode} onSelect={applyPreset} />
          {!detail && !loading ? (
            <div className="ai-chat-empty-state card">
              <h2>Nenhuma conversa selecionada</h2>
              <p>Digite uma mensagem para criar uma conversa ou selecione uma conversa na lateral.</p>
            </div>
          ) : null}
          <ChatMessages messages={detail?.messages ?? []} loading={sending} onCopy={(content) => void copyResponse(content)} />
          <ChatComposer
            disabled={composerDisabled}
            value={composer}
            onValueChange={setComposer}
            onSend={sendMessage}
            isSending={sending}
          />
        </section>
      </div>
    </div>
  );
}
