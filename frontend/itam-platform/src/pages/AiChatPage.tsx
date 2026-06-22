import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Sparkles } from "lucide-react";

import { AiChatIntegrationPanel } from "@/components/ai-chat/AiChatIntegrationPanel";
import { ChatComposer } from "@/components/ai-chat/ChatComposer";
import { ChatMessages } from "@/components/ai-chat/ChatMessages";
import { ConversationList } from "@/components/ai-chat/ConversationList";
import { PromptPresets } from "@/components/ai-chat/PromptPresets";
import type { ChatAttachmentDraft } from "@/components/ai-chat/types";
import { HermesStatusPill } from "@/components/brand/HermesStatusPill";
import { SentinelSectionHeader } from "@/components/brand/SentinelSectionHeader";
import { ApiError, api, mapAiChatError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { AiChatConversation, AiChatConversationDetail, AiChatMode, AiChatProviderHealth } from "@/lib/types";

type AiChatErrorState = {
  error: ApiError;
  context?: string;
};

const HIDDEN_CONVERSATIONS_KEY = "ai-chat:hidden-conversations:v1";
const MAX_ATTACHMENT_PREVIEW_CHARS = 1600;

const TEXT_ATTACHMENT_EXTENSIONS = new Set([
  ".txt",
  ".md",
  ".csv",
  ".json",
  ".yaml",
  ".yml",
  ".xml",
  ".log",
  ".ts",
  ".tsx",
  ".js",
  ".jsx",
  ".py",
  ".css",
  ".html",
  ".htm",
  ".sql",
  ".ini",
]);

function toApiError(error: unknown, fallbackMessage: string) {
  return error instanceof ApiError ? error : new ApiError(fallbackMessage, 0, null);
}

function createAttachmentId() {
  return globalThis.crypto?.randomUUID?.() ?? `attachment-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function formatBytes(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function readHiddenConversationIds() {
  if (typeof window === "undefined") {
    return [] as string[];
  }
  try {
    const raw = window.localStorage.getItem(HIDDEN_CONVERSATIONS_KEY);
    if (!raw) {
      return [] as string[];
    }
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) {
      return [] as string[];
    }
    return parsed.filter((value): value is string => typeof value === "string");
  } catch {
    return [] as string[];
  }
}

function isTextAttachment(file: File) {
  const lowerName = file.name.toLowerCase();
  return file.type.startsWith("text/") || Array.from(TEXT_ATTACHMENT_EXTENSIONS).some((extension) => lowerName.endsWith(extension));
}

function isImageAttachment(file: File) {
  return file.type.startsWith("image/");
}

async function buildAttachmentDraft(file: File): Promise<ChatAttachmentDraft> {
  const category: ChatAttachmentDraft["category"] = isTextAttachment(file) ? "text" : isImageAttachment(file) ? "image" : "binary";
  let preview: string | null = null;
  let note = "Anexo local pronto para entrar no contexto textual do chat.";

  if (category === "text") {
    const text = await file.text();
    preview = text.length > MAX_ATTACHMENT_PREVIEW_CHARS ? `${text.slice(0, MAX_ATTACHMENT_PREVIEW_CHARS)}\n\n… prévia truncada …` : text;
    note = text.length > MAX_ATTACHMENT_PREVIEW_CHARS
      ? `Conteúdo textual truncado em ${MAX_ATTACHMENT_PREVIEW_CHARS} caracteres para evitar prompts excessivos.`
      : "Conteúdo textual pronto para ser incorporado ao contexto do chat.";
  } else if (category === "image") {
    note = "Imagem adicionada como referência local. Sem upload binário ao backend.";
  } else {
    note = "Arquivo binário mantido apenas como referência local. Nenhum upload é enviado ao backend.";
  }

  return {
    id: createAttachmentId(),
    file,
    name: file.name,
    size: file.size,
    type: file.type || "application/octet-stream",
    category,
    preview,
    note,
  };
}

function buildAttachmentContext(attachments: ChatAttachmentDraft[]) {
  if (attachments.length === 0) {
    return "";
  }

  const sections = attachments.map((attachment) => {
    const preview = attachment.preview ? `Prévia textual:\n${attachment.preview}` : attachment.note;
    return [
      `Arquivo local: ${attachment.name}`,
      `Tipo: ${attachment.type || "desconhecido"}`,
      `Tamanho: ${formatBytes(attachment.size)}`,
      `Categoria: ${attachment.category}`,
      preview,
    ].join("\n");
  });

  return [
    "[Contexto local de anexos - sem upload no backend]",
    "Os anexos abaixo foram preparados no frontend para enriquecer o prompt do chat.",
    ...sections,
  ].join("\n\n");
}

function composeOutgoingMessage(content: string, attachments: ChatAttachmentDraft[]) {
  const attachmentContext = buildAttachmentContext(attachments);
  if (!attachmentContext) {
    return content.trim();
  }
  return `${content.trim()}\n\n${attachmentContext}`;
}

function findFirstVisibleConversation(
  conversations: AiChatConversation[],
  hiddenConversationIds: string[],
  excludedId?: string | null,
) {
  return conversations.find((conversation) => conversation.id !== excludedId && !hiddenConversationIds.includes(conversation.id)) ?? null;
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
  const [isPreparingAttachments, setIsPreparingAttachments] = useState(false);
  const [errorState, setErrorState] = useState<AiChatErrorState | null>(null);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);
  const [providerHealth, setProviderHealth] = useState<AiChatProviderHealth | null>(null);
  const [attachments, setAttachments] = useState<ChatAttachmentDraft[]>([]);
  const [hiddenConversationIds, setHiddenConversationIds] = useState<string[]>(readHiddenConversationIds);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.setItem(HIDDEN_CONVERSATIONS_KEY, JSON.stringify(hiddenConversationIds));
  }, [hiddenConversationIds]);

  const hiddenConversationSet = useMemo(() => new Set(hiddenConversationIds), [hiddenConversationIds]);
  const visibleConversations = useMemo(() => conversations.filter((conversation) => !hiddenConversationSet.has(conversation.id)), [conversations, hiddenConversationSet]);
  const hiddenConversations = useMemo(() => conversations.filter((conversation) => hiddenConversationSet.has(conversation.id)), [conversations, hiddenConversationSet]);
  const providerLabel = providerHealth
    ? `${providerHealth.provider}${providerHealth.model ? ` (${providerHealth.model})` : ""}`
    : null;
  const attachmentContext = useMemo(() => buildAttachmentContext(attachments), [attachments]);
  const outgoingMessagePreview = useMemo(() => composeOutgoingMessage(composer, attachments), [attachments, composer]);
  const composerDisabled = loading || sending || isPreparingAttachments || (providerHealth ? !providerHealth.enabled : false);
  const isChatDisabled = providerHealth ? !providerHealth.enabled : false;
  const modeLabels: Record<AiChatMode, string> = {
    general: "Geral",
    fix_text: "Corrigir texto",
    draft_ticket: "Abertura ITIL",
    update_ticket: "Atualização",
    resolution: "Solução aplicada",
    summarize: "Resumir",
    improve_tone: "Melhorar tom",
    service_macro: "Macro",
    asset_guidance: "Orientação de ativo",
  };

  async function refreshConversations(nextSelectedId?: string | null, shouldClearComposer = true) {
    if (!token) {
      return;
    }
    const items = await api.aiChatConversations(token);
    setConversations(items);
    const nextSelected = nextSelectedId ?? selectedId;
    const targetId = nextSelected && items.some((conversation) => conversation.id === nextSelected)
      ? nextSelected
      : findFirstVisibleConversation(items, hiddenConversationIds)?.id ?? null;

    setSelectedId(targetId);
    if (targetId) {
      setDetail(await api.aiChatConversation(token, targetId));
    } else {
      setDetail(null);
    }
    if (shouldClearComposer) {
      setComposer("");
      setAttachments([]);
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
    if (!token || loading || sending || isPreparingAttachments) {
      return;
    }
    setLoading(true);
    setErrorState(null);
    try {
      const conversation = await api.aiChatCreateConversation(token, { title: "Nova conversa" });
      setSelectedId(conversation.id);
      setDetail(conversation);
      await refreshConversations(conversation.id, false);
      setComposer("");
      setAttachments([]);
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
      setAttachments([]);
    } catch (err: unknown) {
      setErrorState({ error: toApiError(err, "Erro desconhecido ao abrir conversa.") });
    } finally {
      setLoading(false);
    }
  }

  function hideConversationLocally(id: string) {
    if (hiddenConversationIds.includes(id)) {
      return;
    }
    const nextHiddenConversationIds = [...hiddenConversationIds, id];
    setHiddenConversationIds(nextHiddenConversationIds);
    if (selectedId === id) {
      const nextVisibleConversation = findFirstVisibleConversation(conversations, nextHiddenConversationIds, id);
      if (nextVisibleConversation) {
        void selectConversation(nextVisibleConversation.id);
      } else {
        setSelectedId(null);
        setDetail(null);
        setComposer("");
        setAttachments([]);
      }
    }
  }

  function restoreConversationLocally(id: string) {
    setHiddenConversationIds((current) => current.filter((conversationId) => conversationId !== id));
  }

  async function addAttachments(files: FileList | File[]) {
    if (!files.length) {
      return;
    }
    setIsPreparingAttachments(true);
    setErrorState(null);
    try {
      const drafts = await Promise.all(Array.from(files).map((file) => buildAttachmentDraft(file)));
      setAttachments((current) => [...current, ...drafts]);
    } catch (err: unknown) {
      setErrorState({ error: toApiError(err, "Não foi possível processar um ou mais anexos locais.") });
    } finally {
      setIsPreparingAttachments(false);
    }
  }

  function removeAttachment(id: string) {
    setAttachments((current) => current.filter((attachment) => attachment.id !== id));
  }

  function clearAttachments() {
    setAttachments([]);
  }

  async function sendMessage(content: string) {
    if (!token || !providerHealth?.enabled || loading || sending || isPreparingAttachments) {
      return;
    }

    const outboundContent = composeOutgoingMessage(content, attachments);
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
              content: outboundContent,
              created_at: new Date().toISOString(),
              provider: null,
              model: null,
            }
          ]
        }) : prev);
      }

      const nextDetail = await api.aiChatSendMessage(token, conversationId, outboundContent, selectedMode);
      setDetail(nextDetail);
      await refreshConversations(conversationId, true);
      setAttachments([]);
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

  function applyPreset(preset: { mode: AiChatMode; text: string }) {
    setSelectedMode(preset.mode);
    setComposer((current) => current.startsWith(preset.text) ? current : `${preset.text}${current}`);
  }

  const mappedError = errorState ? mapAiChatError(errorState.error) : null;
  const payloadChars = outgoingMessagePreview.length;
  const attachmentChars = attachmentContext.length;
  const activeConversation = selectedId ? conversations.find((conversation) => conversation.id === selectedId) ?? detail : detail;

  if (!token) {
    return (
      <div className="ai-chat-page">
        <SentinelSectionHeader
          chips={(
            <>
              <HermesStatusPill state="Offline">Sessão ausente</HermesStatusPill>
              <HermesStatusPill state="Somente leitura">Sem autenticação</HermesStatusPill>
            </>
          )}
          eyebrow="IA Assistiva"
          subtitle="Faça login para acessar o chat assistivo."
          title="IA Assistiva"
        />
        <div className="ai-chat-empty-state card">
          <AlertTriangle size={18} />
          <div>
            <strong>Sessão ausente</strong>
            <p>Entre novamente no sistema para usar o chat.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-chat-page">
      <SentinelSectionHeader
        chips={(
          <>
            <HermesStatusPill state={isChatDisabled ? "Offline" : "Online"}>{providerHealth?.enabled ? "IA ativa" : "IA inativa"}</HermesStatusPill>
            <HermesStatusPill state="Somente leitura">Sem upload real</HermesStatusPill>
            <HermesStatusPill state="Somente leitura">Contexto local de anexos</HermesStatusPill>
          </>
        )}
        eyebrow="IA Assistiva"
        subtitle="Conversa em tempo real com histórico lateral, anexos locais e painel de integração transparente. A IA não executa ações no sistema. Use apenas para apoio textual."
        title="IA Assistiva"
      />

      {providerLabel && (
        <div className="ai-chat-provider-badge" title={`Provider ${providerLabel} - Status: ${providerHealth?.status ?? "indisponível"}`}>
          {providerLabel}
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

      <div className="ai-chat-layout">
        <ConversationList
          conversations={visibleConversations}
          hiddenConversations={hiddenConversations}
          selectedId={selectedId}
          loading={loading || sending || isPreparingAttachments}
          onSelect={(id) => void selectConversation(id)}
          onNewConversation={() => void createConversation()}
          onHideConversation={hideConversationLocally}
          onRestoreConversation={restoreConversationLocally}
        />

        <section className="ai-chat-thread card">
          <div className="ai-chat-thread-header">
            <div>
              <p className="ai-chat-thread-eyebrow">Fluxo principal</p>
              <h2>{activeConversation?.title || "Nova conversa"}</h2>
              <div className="ai-chat-thread-meta">
                <span>{selectedMode === "general" ? "Modo geral" : modeLabels[selectedMode]}</span>
                <span>{detail?.messages.length ?? 0} mensagens</span>
                <span>{attachments.length} anexos locais</span>
              </div>
            </div>
            <Sparkles aria-hidden="true" size={18} />
          </div>

          <PromptPresets selectedMode={selectedMode} onSelect={applyPreset} />

          {!detail && !loading ? (
            <div className="ai-chat-empty-state card">
              <h2>Nenhuma conversa selecionada</h2>
              <p>Crie uma conversa na lateral ou envie uma mensagem para iniciar um novo histórico.</p>
            </div>
          ) : null}

          {loading && !detail ? (
            <div className="ai-chat-empty-state card">
              <h2>Carregando conversa</h2>
              <p>Buscando histórico, mensagens e estado atual.</p>
            </div>
          ) : (
            <ChatMessages messages={detail?.messages ?? []} loading={sending} onCopy={(content) => void copyResponse(content)} />
          )}

          <div className="ai-chat-thread-footer">
            <ChatComposer
              disabled={composerDisabled}
              value={composer}
              onValueChange={setComposer}
              onSend={sendMessage}
              isSending={sending}
              attachments={attachments}
              isPreparingAttachments={isPreparingAttachments}
              attachmentContextChars={attachmentChars}
              outgoingChars={payloadChars}
              onFilesSelected={addAttachments}
              onRemoveAttachment={removeAttachment}
              onClearAttachments={clearAttachments}
            />
          </div>
        </section>

        <AiChatIntegrationPanel
          providerHealth={providerHealth}
          selectedMode={selectedMode}
          conversationCount={visibleConversations.length}
          hiddenConversationCount={hiddenConversations.length}
          attachmentCount={attachments.length}
          attachmentContextChars={attachmentChars}
          outgoingChars={payloadChars}
          isChatDisabled={isChatDisabled}
          attachmentsReady={!isPreparingAttachments}
          providerLabel={providerLabel}
        />
      </div>
    </div>
  );
}
