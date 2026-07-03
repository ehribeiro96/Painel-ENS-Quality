import { AlertTriangle, Bot, ShieldAlert, Sparkles } from "lucide-react";
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

  const healthTone = useMemo(() => {
    if (healthState === "loading") return "warning";
    if (healthState === "error") return "warning";
    if (health?.enabled && health.configured) return "success";
    return "warning";
  }, [health, healthState]);

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
      if (autoSelect && !currentConversationId && nextSelectedId) {
        setSearchParams({ chat: nextSelectedId }, { replace: true });
      }
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
    if (!token || currentConversationId || conversations.length === 0) {
      return;
    }

    setSearchParams({ chat: conversations[0].id }, { replace: true });
  }, [conversations, currentConversationId, setSearchParams, token]);

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
      <ChatConversationSidebar
        conversations={conversations}
        selectedConversationId={currentConversationId}
        previewByConversationId={previewByConversationId}
        loading={loadingHistory}
        query={query}
        onQueryChange={setQuery}
        onSelectConversation={(conversationId) => void handleSelectConversation(conversationId)}
        onNewConversation={() => void handleOpenNewConversation()}
        onReload={() => void handleReload()}
        onRenameConversation={(conversationId, title) => void handleRenameConversation(conversationId, title)}
        onDeleteConversation={(conversationId) => void handleDeleteConversation(conversationId)}
        creatingConversation={sending}
      />

      <section className="flex min-w-0 flex-col gap-4 rounded-[28px] border border-white/10 bg-white/[0.04] p-4 shadow-[0_20px_60px_-26px_rgba(0,0,0,0.75)] md:p-5">
        <header className="flex flex-wrap items-start justify-between gap-3">
          <div className="max-w-3xl">
            <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-cyan-200/70">Chat IA</p>
            <h2 className="mt-1 text-2xl font-semibold tracking-tight text-slate-50">Hermes real no centro da operação</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              {selectedConversation?.title ?? "Nova conversa"} com histórico, novas conversas, exclusão confirmada e anexos locais honestos.
            </p>
          </div>

          <div className="grid gap-2 sm:grid-cols-2">
            <div className="rounded-[22px] border border-white/10 bg-slate-950/40 px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">Status</p>
              <p className="mt-1 text-sm font-medium text-slate-100">{healthLabel}</p>
              <p className="text-xs text-slate-400">
                {healthState === "ready" ? `provider ${provider} • ${model}` : "Conferindo provider real"}
              </p>
            </div>
            <div className="rounded-[22px] border border-white/10 bg-slate-950/40 px-4 py-3">
              <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">Conversas</p>
              <p className="mt-1 text-sm font-medium text-slate-100">{conversations.length}</p>
              <p className="text-xs text-slate-400">{messages.length} mensagem(ns) carregada(s)</p>
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
            <div className="rounded-[28px] border border-dashed border-white/15 bg-slate-950/35 p-6">
              <div className="space-y-6">
                <div className="min-w-0 space-y-4">
                  <div className="inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-400/10 px-3 py-2 text-xs font-medium text-cyan-100">
                    <Sparkles className="h-4 w-4" />
                    Pronto para operar
                  </div>
                  <h3 className="max-w-3xl text-pretty text-2xl font-semibold leading-tight text-slate-50">
                    Envie uma pergunta ou use uma sugestão rápida.
                  </h3>
                  <p className="max-w-3xl text-sm leading-6 text-slate-300">
                    O histórico fica na lateral, o composer suporta arquivos e o caminho de sucesso responde com Hermes real.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {CHAT_SUGGESTIONS.map((suggestion, index) => (
                      <button
                        key={`${suggestion.label}-${index}`}
                        type="button"
                        className="max-w-full rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 transition-colors hover:border-cyan-300/30 hover:bg-cyan-400/10"
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
                    suggestions={CHAT_SUGGESTIONS}
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
                suggestions={CHAT_SUGGESTIONS}
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
