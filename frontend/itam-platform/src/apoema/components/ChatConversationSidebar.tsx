import { useMemo, useState } from "react";
import { Bot, MessageSquarePlus, MoreVertical, Pencil, RefreshCcw, Search, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import type { AiChatConversation } from "@/lib/types";

type Props = {
  conversations: AiChatConversation[];
  selectedConversationId: string | null;
  previewByConversationId: Record<string, string>;
  loading: boolean;
  query: string;
  onQueryChange: (value: string) => void;
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void | Promise<void>;
  onReload: () => void | Promise<void>;
  onRenameConversation: (conversationId: string, title: string) => void | Promise<void>;
  onDeleteConversation: (conversationId: string) => void | Promise<void>;
  creatingConversation?: boolean;
};

function formatConversationTime(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function normalize(text: string) {
  return text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function formatProviderLabel(provider: string | undefined) {
  const value = (provider ?? "").trim();
  if (!value || /mock|fallback|demo|test|beta/i.test(value)) {
    return "Apoema";
  }
  if (value.toLowerCase() === "hermes") {
    return "Hermes";
  }
  return value;
}

export function ChatConversationSidebar({
  conversations,
  selectedConversationId,
  previewByConversationId,
  loading,
  query,
  onQueryChange,
  onSelectConversation,
  onNewConversation,
  onReload,
  onRenameConversation,
  onDeleteConversation,
  creatingConversation = false,
}: Props) {
  const [renameTarget, setRenameTarget] = useState<AiChatConversation | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<AiChatConversation | null>(null);

  const filteredConversations = useMemo(() => {
    return conversations.filter((conversation) => {
      if (!query.trim()) {
        return true;
      }
      const searchable = [conversation.title ?? "Nova conversa", conversation.provider, conversation.model ?? "", previewByConversationId[conversation.id] ?? ""]
        .join(" ")
        .toLowerCase();
      return normalize(searchable).includes(normalize(query.trim()));
    });
  }, [conversations, previewByConversationId, query]);

  return (
    <>
      <aside className="flex h-full min-h-0 w-full min-w-0 flex-col rounded-[28px] border border-white/10 bg-white/[0.04] p-3 shadow-[0_20px_60px_-26px_rgba(0,0,0,0.75)]">
        <div className="flex min-w-0 items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-cyan-200/70">Conversas</p>
            <h2 className="mt-1 truncate text-lg font-semibold text-slate-50">{conversations.length} conversa{conversations.length === 1 ? "" : "s"}</h2>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            aria-label="Recarregar"
            title="Recarregar conversas"
            className="h-10 w-10 shrink-0 rounded-2xl border border-transparent text-slate-400 hover:border-white/10 hover:bg-white/[0.06] hover:text-slate-100 focus-visible:ring-cyan-300/40"
            onClick={() => void onReload()}
            disabled={loading}
          >
            <RefreshCcw className="h-4 w-4" />
            <span className="sr-only">Recarregar</span>
          </Button>
        </div>

        <div className="mt-3 grid gap-2">
          <Button
            type="button"
            className="h-10 rounded-2xl bg-cyan-400 text-slate-950 shadow-[0_16px_40px_-20px_rgba(34,211,238,0.75)] hover:bg-cyan-300"
            onClick={() => void onNewConversation()}
            disabled={creatingConversation}
          >
            <MessageSquarePlus className="h-4 w-4" />
            {creatingConversation ? "Criando..." : "Nova conversa"}
          </Button>

          <label className="flex min-h-10 items-center gap-2 rounded-2xl border border-white/10 bg-slate-950/50 px-3 py-2 text-slate-300 focus-within:border-cyan-300/30 focus-within:ring-2 focus-within:ring-cyan-300/15">
            <Search className="h-4 w-4 shrink-0 text-slate-500" />
            <input
              value={query}
              onChange={(event) => onQueryChange(event.target.value)}
              placeholder="Filtrar conversas"
              aria-label="Filtrar conversas"
              className="w-full bg-transparent text-sm outline-none placeholder:text-slate-500"
            />
          </label>
        </div>

        <div
          className="mt-3 min-h-0 flex-1 space-y-2 overflow-y-auto pr-1 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden"
          aria-label="Lista de conversas"
        >
          {filteredConversations.length === 0 ? (
            <div className="rounded-[22px] border border-white/10 bg-slate-950/40 p-4 text-sm text-slate-400">
              Nenhuma conversa corresponde ao filtro.
            </div>
          ) : (
            filteredConversations.map((conversation) => {
              const selected = conversation.id === selectedConversationId;
              const preview = previewByConversationId[conversation.id] ?? conversation.title ?? "Nova conversa";

              return (
                <div
                  key={conversation.id}
                  className={cn(
                    "group rounded-[20px] border p-2.5 transition-colors",
                    selected ? "border-cyan-300/20 bg-cyan-400/10" : "border-white/10 bg-slate-950/35 hover:bg-white/5",
                  )}
                >
                  <div className="flex items-start gap-2">
                    <button
                      type="button"
                      onClick={() => onSelectConversation(conversation.id)}
                      className="flex min-w-0 flex-1 items-start gap-3 rounded-xl text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/35"
                      aria-current={selected ? "true" : undefined}
                    >
                      <span className={cn("mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl ring-1 ring-inset", selected ? "bg-cyan-300/15 ring-cyan-200/20" : "bg-white/5 ring-white/10")}>
                        <Bot className={cn("h-4 w-4", selected ? "text-cyan-100" : "text-slate-300")} />
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-sm font-medium text-slate-100">{conversation.title || "Nova conversa"}</span>
                        <span className="mt-1 block truncate text-xs text-slate-400">{preview}</span>
                        <span className="mt-1 block truncate text-[11px] uppercase tracking-[0.18em] text-slate-500">
                          {conversation.model ? `${conversation.model} • ` : ""}
                          {formatConversationTime(conversation.updated_at)}
                        </span>
                      </span>
                    </button>

                    <div className="flex shrink-0 items-center">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            aria-label={`Ações da conversa ${conversation.title || "Nova conversa"}`}
                            className="h-9 w-9 rounded-full text-slate-300 hover:bg-white/10 hover:text-slate-50"
                          >
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="border-white/10 bg-slate-950 text-slate-100">
                          <DropdownMenuItem
                            onClick={() => {
                              setRenameTarget(conversation);
                              setRenameValue(conversation.title ?? "Nova conversa");
                            }}
                          >
                            <Pencil className="mr-2 h-4 w-4" />
                            Renomear
                          </DropdownMenuItem>
                          <DropdownMenuSeparator className="bg-white/10" />
                          <DropdownMenuItem
                            className="text-rose-100 focus:bg-rose-500/10 focus:text-rose-50"
                            onClick={() => setDeleteTarget(conversation)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Excluir
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </aside>

      <Dialog
        open={Boolean(renameTarget)}
        onOpenChange={(open) => {
          if (!open) {
            setRenameTarget(null);
            setRenameValue("");
          }
        }}
      >
        <DialogContent className="border-white/10 bg-slate-950 text-slate-100">
          <DialogHeader>
            <DialogTitle>Renomear conversa</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <label className="space-y-2 text-sm text-slate-300">
              Novo título
              <Input
                value={renameValue}
                onChange={(event) => setRenameValue(event.target.value)}
                className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500"
                placeholder="Nova conversa"
              />
            </label>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="ghost"
              className="rounded-2xl text-slate-200 hover:bg-white/5"
              onClick={() => {
                setRenameTarget(null);
                setRenameValue("");
              }}
            >
              Cancelar
            </Button>
            <Button
              type="button"
              className="rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300"
              onClick={async () => {
                if (!renameTarget || !renameValue.trim()) {
                  return;
                }
                await onRenameConversation(renameTarget.id, renameValue.trim());
                setRenameTarget(null);
                setRenameValue("");
              }}
            >
              Salvar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => {
          if (!open) {
            setDeleteTarget(null);
          }
        }}
      >
        <AlertDialogContent className="border-white/10 bg-slate-950 text-slate-100">
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir conversa?</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-300">
              A exclusão remove a conversa de forma persistente. Após confirmar, ela não deve reaparecer ao recarregar a página.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10">
              Cancelar
            </AlertDialogCancel>
            <AlertDialogAction
              className="rounded-2xl bg-rose-500 text-white hover:bg-rose-400"
              onClick={async () => {
                if (!deleteTarget) {
                  return;
                }
                await onDeleteConversation(deleteTarget.id);
                setDeleteTarget(null);
              }}
            >
              Excluir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
