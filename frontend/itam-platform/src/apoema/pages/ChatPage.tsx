import { AlertTriangle, Bot, History, ShieldAlert, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { toast } from "sonner";

import { ChatComposer, type ComposerAttachment } from "../components/ChatComposer";
import { ChatConversationSidebar } from "../components/ChatConversationSidebar";
import { ChatMessage } from "../components/ChatMessage";
import { ApoemaChatBridgeAdapter, type ApoemaChatMessage, type ApoemaChatSession } from "../adapters/ApoemaChatBridgeAdapter";
import { useAuth } from "@/lib/auth";
import { validateAttachmentFile } from "@/lib/chatAttachments";
import { createFilePart, createTextPart, serializeChatMessageContent } from "@/lib/chatMessageParts";
import type { AiChatConversation, AiChatMessage, AiChatProviderHealth } from "@/lib/types";
import { ApoemaApiError } from "../types";

const CHAT_SUGGESTIONS = [
  { label: "Consultar ativo", prompt: "Quero consultar um ativo e entender o histórico recente." },
  { label: "Resumir movimentações", prompt: "Resuma as movimentações recentes e destaque pontos de atenção." },
  { label: "Gerar macro", prompt: "Crie uma macro operacional objetiva para uma movimentação segura." },
  { label: "Analisar importação", prompt: "Analise uma importação e liste os pontos que merecem revisão." },
];

type BannerTone = "warning" | "danger";

type Banner = {
  tone: BannerTone;
  title: string;
  message: string;
};

function shortenPrompt(value: string, limit = 64) {
  const compact = value.replace(/\s+/g, " ").trim();
  if (!compact) {
    return "Nova conversa";
  }
  return compact.length > limit ? `${compact.slice(0, limit - 1).trimEnd()}…` : compact;
}

function describeApiError(error: unknown): Banner {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required" || error.status === 401) {
      return {
        tone: "danger",
        title: "Sessão expirada",
        message: "Sua sessão expirou ou não foi autenticada. Faça login novamente para usar o chat.",
      };
    }
    if (error.kind === "forbidden" || error.status === 403) {
      return {
        tone: "danger",
        title: "Sem permissão",
        message: "Você não tem permissão para usar este recurso.",
      };
    }
    if (error.kind === "rate_limited" || error.status === 429) {
      return {
        tone: "warning",
        title: "Limite temporário atingido",
        message: "Limite temporário atingido. Aguarde alguns instantes e tente novamente.",
      };
    }
    if (error.kind === "backend_error" || (error.status ?? 0) >= 500) {
      return {
        tone: "danger",
        title: "Backend indisponível",
        message: "O backend do chat retornou erro. Tente novamente em instantes.",
      };
    }
  }

  return {
    tone: "danger",
    title: "Erro inesperado",
    message: "Não foi possível concluir a operação. Tente novamente em instantes.",
  };
}

function toConversation(session: ApoemaChatSession, provider: string, model: string | null, userId: string): AiChatConversation {
  return {
    id: session.id,
    user_id: userId,
    title: session.title,
    provider,
    model,
    system_prompt_version: "apoema-chat-shell",
    created_at: session.created_at,
    updated_at: session.updated_at,
  };
}

function toRenderableMessage(message: ApoemaChatMessage, conversationId: string, provider: string, model: string | null): AiChatMessage {
  return {
    id: message.id,
    conversation_id: conversationId,
    role: message.role,
    content: message.content,
    provider,
    model,
    created_at: message.created_at,
  };
}

function replaceLastUserMessageContent(messages: AiChatMessage[], content: string) {
  const next = [...messages];
  for (let index = next.length - 1; index >= 0; index -= 1) {
    if (next[index]?.role === "user") {
      next[index] = { ...next[index], content };
      break;
    }
  }
  return next;
}

function isSensitiveAttachmentName(fileName: string) {
  return /\.(env|key|pem|p12|pfx|crt|cer|der|jks|keystore|secret|credentials?|token|config)$/i.test(fileName) || /(^|[\W_])(token|secret|credential|passwd|password)([\W_]|$)/i.test(fileName);
}

async function buildAttachmentDraft(file: File, id: string): Promise<ComposerAttachment> {
  const kind: ComposerAttachment["kind"] = file.type.startsWith("image/") ? "image" : "file";
  const previewUrl = URL.createObjectURL(file);
  let previewText: string | null = null;

  if (!file.type.startsWith("image/") && file.size <= 96_000) {
    try {
      const text = await file.text();
      previewText = text.slice(0, 1000).trim() || null;
    } catch {
      previewText = null;
    }
  }

  return { id, file, kind, previewUrl, previewText };
}

export function ChatPage() {
  const { token, user, loading: authLoading } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const currentConversationId = searchParams.get("chat");
  const newConversationRequested = searchParams.get("new") === "1";
  const [conversations, setConversations] = useState<AiChatConversation[]>([]);
  const [messages, setMessages] = useState<AiChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [query, setQuery] = useState("");
  const [attachments, setAttachments] = useState<ComposerAttachment[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [health, setHealth] = useState<AiChatProviderHealth | null>(null);
  const [healthState, setHealthState] = useState<"loading" | "ready" | "error">("loading");
  const [banner, setBanner] = useState<Banner | null>(null);
  const [mobileHistoryOpen, setMobileHistoryOpen] = useState(false);

  const provider = health?.provider && !/mock|fallback/i.test(health.provider) ? health.provider : "hermes";
  const model = health?.model ?? "hermes-agent";

  const selectedConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === currentConversationId) ?? null,
    [conversations, currentConversationId],
  );

  const previewByConversationId = useMemo(() => {
    const previews: Record<string, string> = {};
    for (const conversation of conversations) {
      previews[conversation.id] = conversation.title ?? "Nova conversa";
    }
    if (currentConversationId) {
      const latest = [...messages].at(-1)?.content?.trim();
      if (latest) {
        previews[currentConversationId] = shortenPrompt(latest, 96);
      }
    }
    return previews;
  }, [conversations, currentConversationId, messages]);

  const healthLabel = useMemo(() => {
    if (healthState === "loading") return "Checando Hermes";
    if (healthState === "error") return "Indisponível";
    if (health?.enabled && health.configured) return "Hermes online";
    return "Atenção";
  }, [health, healthState]);

  async function loadHealth() {
    if (!token) return;

    setHealthState("loading");
    try {
      const nextHealth = await ApoemaChatBridgeAdapter.health(token);
      setHealth(nextHealth);
      setHealthState("ready");
    } catch (error) {
      setHealth(null);
      setHealthState("error");
      setBanner(describeApiError(error));
    }
  }

  async function loadConversations(
    preferredConversationId?: string | null,
    options: { autoSelect?: boolean } = {},
  ): Promise<AiChatConversation[]> {
    if (!token) return [];

    const autoSelect = options.autoSelect ?? true;
    setLoadingHistory(true);
    try {
      const nextConversations = await ApoemaChatBridgeAdapter.listSessions(token);
      const nextRenderable = nextConversations.map((conversation) => toConversation(conversation, provider, health?.model ?? null, user?.id ?? "apoema-user"));
      setConversations(nextRenderable);

      const nextSelectedId = preferredConversationId ?? (autoSelect ? nextRenderable[0]?.id : null) ?? null;
      if (!nextSelectedId || !autoSelect) {
        setMessages([]);
      }
      return nextRenderable;
    } catch (error) {
      setConversations([]);
      setBanner(describeApiError(error));
      return [];
    } finally {
      setLoadingHistory(false);
    }
  }

  async function loadMessages(conversationId: string) {
    if (!token) return;

    setLoadingMessages(true);
    try {
      const nextMessages = await ApoemaChatBridgeAdapter.listMessages(token, conversationId);
      setMessages(nextMessages.map((message) => toRenderableMessage(message, conversationId, provider, health?.model ?? null)));
    } catch (error) {
      setMessages([]);
      setBanner(describeApiError(error));
    } finally {
      setLoadingMessages(false);
    }
  }

  useEffect(() => {
    if (!token) return;

    void loadHealth();
    if (newConversationRequested) {
      setMessages([]);
      setInput("");
      setAttachments([]);
      setBanner(null);
      void loadConversations(null, { autoSelect: false });
      return;
    }
    void loadConversations(currentConversationId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, currentConversationId, newConversationRequested]);

  useEffect(() => {
    if (!token) return;
    if (currentConversationId) {
      void loadMessages(currentConversationId);
      return;
    }
    setMessages([]);
  }, [currentConversationId, token]);

  useEffect(() => {
    const latestSearch = new URLSearchParams(window.location.search);
    if (
      !token ||
      currentConversationId ||
      newConversationRequested ||
      latestSearch.has("new") ||
      latestSearch.has("chat") ||
      conversations.length === 0
    ) {
      return;
    }

    setSearchParams({ chat: conversations[0].id }, { replace: true });
  }, [conversations, currentConversationId, newConversationRequested, setSearchParams, token]);

  useEffect(() => {
    return () => {
      attachments.forEach((attachment) => {
        if (attachment.previewUrl?.startsWith("blob:")) {
          URL.revokeObjectURL(attachment.previewUrl);
        }
      });
    };
  }, [attachments]);

  async function handleSelectConversation(conversationId: string) {
    setSearchParams({ chat: conversationId }, { replace: true });
  }

  async function handleOpenNewConversation() {
    setSearchParams({ new: "1" }, { replace: true });
    setMessages([]);
    setInput("");
    setAttachments([]);
    setBanner(null);
  }

  async function handleReload() {
    await loadHealth();
    await loadConversations(currentConversationId);
    if (currentConversationId) {
      await loadMessages(currentConversationId);
    }
  }

  async function handleRenameConversation(conversationId: string, title: string) {
    if (!token) return;
    try {
      await ApoemaChatBridgeAdapter.renameSession(token, conversationId, title);
      await loadConversations(currentConversationId);
    } catch (error) {
      const nextBanner = describeApiError(error);
      setBanner(nextBanner);
      toast.error(nextBanner.title);
    }
  }

  async function handleDeleteConversation(conversationId: string) {
    if (!token) return;
    try {
      await ApoemaChatBridgeAdapter.deleteSession(token, conversationId);
      const nextConversations = await loadConversations(currentConversationId === conversationId ? null : currentConversationId);
      if (currentConversationId === conversationId) {
        const nextConversation = nextConversations[0] ?? null;
        if (nextConversation) {
          setSearchParams({ chat: nextConversation.id }, { replace: true });
          await loadMessages(nextConversation.id);
        } else {
          setSearchParams({}, { replace: true });
          setMessages([]);
        }
      }
    } catch (error) {
      const nextBanner = describeApiError(error);
      setBanner(nextBanner);
      toast.error(nextBanner.title);
    }
  }

  async function handlePickFiles(files: FileList) {
    const incoming = Array.from(files);
    const created: ComposerAttachment[] = [];
    for (const file of incoming) {
      if (isSensitiveAttachmentName(file.name)) {
        toast.error(`Anexo bloqueado: ${file.name}`);
        continue;
      }

      const validation = validateAttachmentFile(file);
      if (!validation.success) {
        toast.error(validation.error);
        continue;
      }

      const id = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;
      // Keep the preview local and honest. Nothing is uploaded here.
      const draft = await buildAttachmentDraft(file, id);
      created.push(draft);
    }

    setAttachments((current) => [...current, ...created]);
  }

  function removeAttachment(id: string) {
    setAttachments((current) => {
      const target = current.find((item) => item.id === id);
      if (target?.previewUrl?.startsWith("blob:")) {
        URL.revokeObjectURL(target.previewUrl);
      }
      return current.filter((item) => item.id !== id);
    });
  }

  function clearAttachments() {
    setAttachments((current) => {
      current.forEach((attachment) => {
        if (attachment.previewUrl?.startsWith("blob:")) {
          URL.revokeObjectURL(attachment.previewUrl);
        }
      });
      return [];
    });
  }

  function buildLocalContent(text: string) {
    const trimmed = text.trim();
    const textPart = trimmed ? [createTextPart(trimmed)] : [];
    const fileParts = attachments.map((attachment) =>
      createFilePart({
        kind: attachment.kind,
        name: attachment.file.name,
        url: attachment.previewUrl ?? "",
        mimeType: attachment.file.type,
      }),
    );
    return serializeChatMessageContent([...textPart, ...fileParts]);
  }

  async function handleSend(content: string) {
    if (!token || !user) return;

    const trimmed = content.trim();
    if (!trimmed && attachments.length === 0) {
      return;
    }

    setSending(true);
    setBanner(null);

    const structuredContent = buildLocalContent(trimmed || "Anexos locais");

    try {
      if (currentConversationId) {
        const nextMessages = await ApoemaChatBridgeAdapter.sendMessage(token, currentConversationId, { content: trimmed || "Anexos locais" });
        const mapped = nextMessages.map((message) => toRenderableMessage(message, currentConversationId, provider, health?.model ?? null));
        setMessages(attachments.length > 0 ? replaceLastUserMessageContent(mapped, structuredContent) : mapped);
        await loadConversations(currentConversationId);
      } else {
        const title = shortenPrompt(trimmed || "Anexos locais");
        const created = await ApoemaChatBridgeAdapter.createSessionAndSendMessage(token, title, { content: trimmed || "Anexos locais" });
        setSearchParams({ chat: created.session.id }, { replace: true });
        const mapped = created.messages.map((message) => toRenderableMessage(message, created.session.id, provider, health?.model ?? null));
        setMessages(attachments.length > 0 ? replaceLastUserMessageContent(mapped, structuredContent) : mapped);
        await loadConversations(created.session.id);
      }
      setInput("");
      clearAttachments();
    } catch (error) {
      const nextBanner = describeApiError(error);
      setBanner(nextBanner);
      toast.error(nextBanner.title);
    } finally {
      setSending(false);
    }
  }

  const isEmptyState = !currentConversationId || messages.length === 0;

  return (
    <div className="grid min-w-0 gap-4 lg:grid-cols-[clamp(240px,22vw,300px)_minmax(0,1fr)]">
      <button
        type="button"
        className="flex h-11 w-full items-center justify-between rounded-2xl border border-white/10 bg-white/[0.04] px-4 text-sm font-medium text-slate-100 transition-colors hover:bg-white/[0.07] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/40 lg:hidden"
        aria-expanded={mobileHistoryOpen}
        aria-controls="apoema-chat-history"
        onClick={() => setMobileHistoryOpen((current) => !current)}
      >
        <span className="inline-flex items-center gap-2">
          <History className="h-4 w-4 text-cyan-200" />
          Conversas
        </span>
        <span className="text-xs font-normal text-slate-400">{conversations.length} conversa{conversations.length === 1 ? "" : "s"}</span>
      </button>

      <div id="apoema-chat-history" className={`min-w-0 ${mobileHistoryOpen ? "block" : "hidden lg:block"}`}>
        <ChatConversationSidebar
          conversations={conversations}
          selectedConversationId={currentConversationId}
          previewByConversationId={previewByConversationId}
          loading={loadingHistory}
          query={query}
          onQueryChange={setQuery}
          onSelectConversation={(conversationId) => {
            setMobileHistoryOpen(false);
            void handleSelectConversation(conversationId);
          }}
          onNewConversation={() => {
            setMobileHistoryOpen(false);
            void handleOpenNewConversation();
          }}
          onReload={() => void handleReload()}
          onRenameConversation={(conversationId, title) => void handleRenameConversation(conversationId, title)}
          onDeleteConversation={(conversationId) => void handleDeleteConversation(conversationId)}
          creatingConversation={sending}
        />
      </div>

      <section className="flex min-w-0 flex-col gap-4 rounded-[28px] border border-white/10 bg-white/[0.04] p-3 shadow-[0_20px_60px_-26px_rgba(0,0,0,0.75)] md:p-5">
        <header>
          <div className="max-w-4xl">
            <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-cyan-200/70">Chat IA</p>
            <h2 className="mt-1 text-xl font-semibold tracking-tight text-slate-50 md:text-2xl">Hermes real no centro da operação</h2>
            <p className="mt-1.5 text-sm leading-6 text-slate-400">
              {selectedConversation?.title ?? "Nova conversa"} com histórico, novas conversas, exclusão confirmada e anexos locais honestos.
            </p>
            <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-400" aria-label="Estado do chat">
              <span className="inline-flex items-center gap-2 text-slate-300">
                <span className={`h-2 w-2 rounded-full ${healthState === "ready" && health?.enabled && health.configured ? "bg-emerald-300" : "bg-amber-300"}`} />
                {healthLabel}
              </span>
              <span>{healthState === "ready" ? `${provider} • ${model}` : "Conferindo provider real"}</span>
              <span>{conversations.length} conversa{conversations.length === 1 ? "" : "s"}</span>
              <span>{messages.length} mensagem{messages.length === 1 ? "" : "s"}</span>
            </div>
          </div>
        </header>

        {banner ? (
          <div
            className={banner.tone === "danger" ? "rounded-[22px] border border-rose-400/20 bg-rose-500/10 p-4 text-rose-100" : "rounded-[22px] border border-amber-400/20 bg-amber-500/10 p-4 text-amber-100"}
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                {banner.tone === "danger" ? <ShieldAlert className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
              </div>
              <div>
                <strong className="block text-sm">{banner.title}</strong>
                <p className="mt-1 text-sm leading-6">{banner.message}</p>
              </div>
            </div>
          </div>
        ) : null}

        <div className="flex min-h-0 flex-1 flex-col gap-4">
          {isEmptyState ? (
            <div className="flex min-h-0 flex-1 flex-col justify-center py-2 md:py-5">
              <div className="space-y-5">
                <div className="min-w-0 space-y-3">
                  <div className="inline-flex items-center gap-2 text-xs font-medium text-cyan-100">
                    <Sparkles className="h-4 w-4" />
                    Pronto para operar
                  </div>
                  <h3 className="max-w-3xl text-pretty text-xl font-semibold leading-tight text-slate-50 md:text-2xl">
                    Envie uma pergunta ou use uma sugestão rápida.
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {CHAT_SUGGESTIONS.map((suggestion, index) => (
                      <button
                        key={`${suggestion.label}-${index}`}
                        type="button"
                        className="max-w-full rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-slate-300 transition-colors hover:border-cyan-300/30 hover:bg-cyan-400/10 hover:text-slate-100"
                        onClick={() => setInput(suggestion.prompt)}
                      >
                        {suggestion.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="min-w-0">
                  <ChatComposer
                    value={input}
                    onChange={setInput}
                    onSubmit={() => void handleSend(input)}
                    onPickSuggestion={(prompt) => setInput(prompt)}
                    suggestions={[]}
                    showSuggestions={false}
                    disabled={authLoading || !token || !user || loadingMessages}
                    isSending={sending}
                    attachments={attachments}
                    onPickFiles={handlePickFiles}
                    onRemoveAttachment={removeAttachment}
                    onClearAttachments={clearAttachments}
                  />
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}

                {sending ? (
                  <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">
                    <Sparkles className="h-4 w-4 animate-pulse text-cyan-100" />
                    Hermes está analisando a solicitação...
                  </div>
                ) : null}
              </div>

              <ChatComposer
                value={input}
                onChange={setInput}
                onSubmit={() => void handleSend(input)}
                onPickSuggestion={(prompt) => setInput(prompt)}
                suggestions={[]}
                showSuggestions={false}
                disabled={authLoading || !token || !user || loadingMessages}
                isSending={sending}
                attachments={attachments}
                onPickFiles={handlePickFiles}
                onRemoveAttachment={removeAttachment}
                onClearAttachments={clearAttachments}
              />
            </>
          )}
        </div>
      </section>
    </div>
  );
}
