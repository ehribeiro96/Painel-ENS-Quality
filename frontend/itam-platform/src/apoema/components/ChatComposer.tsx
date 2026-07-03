import { useEffect, useMemo, useRef, useState } from "react";
import { FileText, Image as ImageIcon, Paperclip, SendHorizonal, Trash2, Upload, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { CHAT_COMPOSER_ACCEPTED_FILE_TYPES } from "@/lib/chatAttachmentPolicy";
import { cn } from "@/lib/utils";
import type { ChatPromptSuggestion } from "./ChatEmptyState";

export type ComposerAttachment = {
  id: string;
  file: File;
  kind: "image" | "file";
  previewUrl?: string;
  previewText?: string | null;
};

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void | Promise<void>;
  onPickSuggestion: (prompt: string) => void;
  suggestions: ChatPromptSuggestion[];
  disabled?: boolean;
  isSending?: boolean;
  placeholder?: string;
  attachments?: ComposerAttachment[];
  onPickFiles?: (files: FileList) => void | Promise<void>;
  onRemoveAttachment?: (id: string) => void;
  onClearAttachments?: () => void;
};

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function attachmentIcon(kind: ComposerAttachment["kind"]) {
  return kind === "image" ? <ImageIcon className="h-4 w-4" /> : <FileText className="h-4 w-4" />;
}

export function ChatComposer({
  value,
  onChange,
  onSubmit,
  onPickSuggestion,
  suggestions,
  disabled = false,
  isSending = false,
  placeholder = "Pergunte sobre ativos, movimentações, macros ou inventário...",
  attachments = [],
  onPickFiles,
  onRemoveAttachment,
  onClearAttachments,
}: Props) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }, [value]);

  useEffect(() => {
    if (!disabled) {
      textareaRef.current?.focus({ preventScroll: true });
    }
  }, [disabled]);

  const canSend = useMemo(() => Boolean(value.trim() || attachments.length > 0), [attachments.length, value]);

  async function submit() {
    if (disabled || isSending || !canSend) {
      return;
    }
    await onSubmit();
  }

  async function handleFiles(files: FileList | null) {
    if (!files || files.length === 0 || !onPickFiles || disabled) {
      return;
    }
    await onPickFiles(files);
  }

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-[28px] border border-white/10 bg-white/[0.04] p-4 shadow-[0_20px_60px_-26px_rgba(0,0,0,0.75)]",
        dragActive && "border-cyan-300/30 bg-cyan-400/10",
        disabled && "opacity-80",
      )}
      onDragEnter={(event) => {
        event.preventDefault();
        if (!disabled) {
          setDragActive(true);
        }
      }}
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) {
          event.dataTransfer.dropEffect = "copy";
          setDragActive(true);
        }
      }}
      onDragLeave={(event) => {
        event.preventDefault();
        if (event.currentTarget === event.target) {
          setDragActive(false);
        }
      }}
      onDrop={async (event) => {
        event.preventDefault();
        setDragActive(false);
        await handleFiles(event.dataTransfer.files);
      }}
    >
      <input
        ref={fileInputRef}
        className="sr-only"
        type="file"
        multiple
        accept={CHAT_COMPOSER_ACCEPTED_FILE_TYPES}
        onChange={async (event) => {
          await handleFiles(event.target.files);
          event.target.value = "";
        }}
      />

      <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-center">
        <div className="flex min-w-0 flex-wrap items-center gap-2">
          {suggestions.map((suggestion, index) => (
            <button
              key={`${suggestion.label}-${index}`}
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-200 transition-colors hover:border-cyan-300/30 hover:bg-cyan-400/10"
              onClick={() => onPickSuggestion(suggestion.prompt)}
            >
              <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-cyan-400/10 text-cyan-100">
                <Paperclip className="h-3 w-3" />
              </span>
              {suggestion.label}
            </button>
          ))}
        </div>
        <div className="text-xs text-slate-400 xl:text-right">
          {isSending ? "Enviando para Hermes..." : "Enter envia. Shift+Enter quebra linha."}
        </div>
      </div>

      {attachments.length > 0 ? (
        <section className="mt-4 space-y-3" aria-label="Anexos locais">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Anexos locais</p>
              <p className="text-sm text-slate-300">Contexto visível no composer antes do envio.</p>
            </div>
            {onClearAttachments ? (
              <Button type="button" variant="ghost" className="rounded-2xl text-slate-200 hover:bg-white/5" onClick={onClearAttachments} disabled={disabled}>
                <Trash2 className="h-4 w-4" />
                Limpar
              </Button>
            ) : null}
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {attachments.map((attachment) => (
              <article key={attachment.id} className="rounded-[22px] border border-white/10 bg-slate-950/50 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 text-sm font-medium text-slate-100">
                      <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-cyan-400/10 text-cyan-100">
                        {attachmentIcon(attachment.kind)}
                      </span>
                      <span className="truncate">{attachment.file.name}</span>
                    </div>
                    <p className="mt-1 text-xs text-slate-400">
                      {formatBytes(attachment.file.size)} • {attachment.file.type || "sem tipo"}
                    </p>
                  </div>
                  {onRemoveAttachment ? (
                    <button
                      type="button"
                      onClick={() => onRemoveAttachment(attachment.id)}
                      className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/5 text-slate-300 transition-colors hover:border-rose-300/20 hover:bg-rose-500/10 hover:text-rose-100"
                      aria-label={`Remover ${attachment.file.name}`}
                    >
                      <X className="h-4 w-4" />
                    </button>
                  ) : null}
                </div>

                {attachment.previewUrl ? (
                  <div className="mt-3 overflow-hidden rounded-2xl border border-white/10">
                    {attachment.kind === "image" ? (
                      <img src={attachment.previewUrl} alt={attachment.file.name} className="h-36 w-full object-cover" />
                    ) : (
                      <a href={attachment.previewUrl} target="_blank" rel="noreferrer" className="block px-3 py-3 text-sm text-cyan-100 hover:underline">
                        Abrir arquivo local
                      </a>
                    )}
                  </div>
                ) : null}

                {attachment.previewText ? (
                  <details className="mt-3 rounded-2xl border border-white/10 bg-white/5 p-3">
                    <summary className="cursor-pointer text-xs font-medium text-slate-200">Prévia textual</summary>
                    <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap break-words text-xs leading-5 text-slate-300">
                      {attachment.previewText}
                    </pre>
                  </details>
                ) : null}
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <div className="mt-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="outline"
              className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10"
              onClick={() => fileInputRef.current?.click()}
              disabled={disabled}
            >
              <Upload className="h-4 w-4" />
              Anexar arquivos
            </Button>
            <span className="text-xs text-slate-400">Arquivos sensíveis são bloqueados antes do envio.</span>
          </div>
          <Button
            type="button"
            className="rounded-2xl bg-cyan-400 px-5 text-slate-950 shadow-[0_16px_40px_-20px_rgba(34,211,238,0.75)] hover:bg-cyan-300"
            onClick={() => void submit()}
            disabled={disabled || isSending || !canSend}
          >
            <SendHorizonal className="h-4 w-4" />
            {isSending ? "Enviando..." : "Enviar"}
          </Button>
        </div>

        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void submit();
            }
          }}
          placeholder={placeholder}
          rows={3}
          disabled={disabled}
          className="min-h-[120px] rounded-[24px] border-white/10 bg-slate-950/60 text-slate-50 placeholder:text-slate-500 focus-visible:border-cyan-300/40 focus-visible:ring-cyan-300/20"
        />
      </div>
    </div>
  );
}
