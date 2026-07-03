import { Bot, Copy, UserRound } from "lucide-react";
import { useMemo, useState } from "react";

import { ChatMessageContent } from "@/components/ChatMessageContent";
import type { AiChatMessage } from "@/lib/types";
import { cn } from "@/lib/utils";

function roleLabel(role: AiChatMessage["role"]) {
  switch (role) {
    case "assistant":
      return "Hermes";
    case "system":
      return "Sistema";
    default:
      return "Você";
  }
}

function formatTimestamp(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

export function ChatMessage({ message }: { message: AiChatMessage }) {
  const [copied, setCopied] = useState(false);
  const isAssistant = message.role === "assistant";
  const icon = isAssistant ? <Bot className="h-4 w-4" /> : <UserRound className="h-4 w-4" />;

  const copiedLabel = useMemo(() => (copied ? "Copiado" : "Copiar"), [copied]);

  async function copyMessage() {
    if (!message.content.trim() || !navigator.clipboard) {
      return;
    }
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  return (
    <article
      className={cn(
        "rounded-[26px] border p-4 shadow-[0_16px_40px_-24px_rgba(0,0,0,0.85)]",
        isAssistant ? "border-white/10 bg-white/[0.04]" : "border-cyan-300/15 bg-cyan-400/8",
      )}
      data-role={message.role}
    >
      <header className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className={cn("flex h-10 w-10 items-center justify-center rounded-2xl ring-1 ring-inset", isAssistant ? "bg-white/5 text-cyan-100 ring-white/10" : "bg-cyan-300/10 text-cyan-50 ring-cyan-200/20")}>
            {icon}
          </span>
          <div>
            <strong className="block text-sm font-medium text-slate-50">{roleLabel(message.role)}</strong>
            <span className="block text-xs text-slate-400">{formatTimestamp(message.created_at)}</span>
          </div>
        </div>
        {isAssistant ? (
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-200 transition-colors hover:border-cyan-300/30 hover:bg-cyan-400/10"
            onClick={() => void copyMessage()}
            disabled={!message.content.trim()}
            aria-label="Copiar resposta"
          >
            <Copy className="h-4 w-4" />
            {copiedLabel}
          </button>
        ) : null}
      </header>

      <div className="mt-4">
        <ChatMessageContent role={message.role} content={message.content} />
      </div>
    </article>
  );
}
