import { Paperclip, SendHorizonal, Trash2, Upload } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import type { ChatAttachmentDraft } from "./types";

type Props = {
  disabled?: boolean;
  value?: string;
  onValueChange?: (value: string) => void;
  onSend: (content: string) => Promise<void> | void;
  isSending?: boolean;
  attachments: ChatAttachmentDraft[];
  isPreparingAttachments?: boolean;
  attachmentContextChars: number;
  outgoingChars: number;
  onFilesSelected: (files: FileList | File[]) => Promise<void> | void;
  onRemoveAttachment: (id: string) => void;
  onClearAttachments: () => void;
};

function formatBytes(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function attachmentIcon(category: ChatAttachmentDraft["category"]) {
  if (category === "image") {
    return "🖼";
  }
  if (category === "binary") {
    return "📦";
  }
  return "📄";
}

export function ChatComposer({
  disabled,
  value,
  onValueChange,
  onSend,
  isSending,
  attachments,
  isPreparingAttachments,
  attachmentContextChars,
  outgoingChars,
  onFilesSelected,
  onRemoveAttachment,
  onClearAttachments,
}: Props) {
  const [internalValue, setInternalValue] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const text = value ?? internalValue;

  useEffect(() => {
    if (!disabled) {
      textareaRef.current?.focus({ preventScroll: true });
    }
  }, [disabled, isSending]);

  function update(next: string) {
    if (onValueChange) {
      onValueChange(next);
    } else {
      setInternalValue(next);
    }
  }

  async function submit() {
    const content = text.trim();
    if (!content || disabled || isPreparingAttachments) {
      return;
    }
    await onSend(content);
  }

  function openPicker() {
    fileInputRef.current?.click();
  }

  async function handleFiles(files: FileList | File[]) {
    if (!files.length) {
      return;
    }
    await onFilesSelected(files);
  }

  const isSendDisabled = Boolean(disabled || isPreparingAttachments || !text.trim());
  const helperText = useMemo(() => {
    if (isPreparingAttachments) {
      return "Preparando anexos locais para o contexto do chat.";
    }
    if (attachments.length > 0) {
      return "Os anexos selecionados entram como contexto textual. Não há upload binário para o backend.";
    }
    return "Use Shift+Enter para quebrar linha. Arquivos podem ser arrastados para este painel.";
  }, [attachments.length, isPreparingAttachments]);

  return (
    <div
      className={dragActive ? "ai-chat-composer drop-active" : disabled ? "ai-chat-composer disabled" : "ai-chat-composer"}
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
        if (disabled) {
          return;
        }
        await handleFiles(event.dataTransfer.files);
      }}
    >
      <input
        ref={fileInputRef}
        className="sr-only"
        type="file"
        multiple
        onChange={async (event) => {
          const files = event.target.files;
          if (files) {
            await handleFiles(files);
            event.target.value = "";
          }
        }}
      />

      {attachments.length > 0 ? (
        <section className="ai-chat-attachments" aria-label="Anexos locais">
          <div className="ai-chat-attachments-header">
            <strong>Anexos locais</strong>
            <button className="button ghost" type="button" onClick={onClearAttachments} disabled={disabled}>
              <Trash2 size={14} />
              Limpar
            </button>
          </div>
          <div className="ai-chat-attachment-list">
            {attachments.map((attachment) => (
              <article className="ai-chat-attachment-card" key={attachment.id}>
                <div className="ai-chat-attachment-card-header">
                  <div>
                    <strong>
                      {attachmentIcon(attachment.category)} {attachment.name}
                    </strong>
                    <span className="ai-chat-attachment-meta">
                      {formatBytes(attachment.size)} • {attachment.type || "sem tipo"}
                    </span>
                  </div>
                  <button className="ai-chat-attachment-remove" type="button" onClick={() => onRemoveAttachment(attachment.id)} aria-label={`Remover ${attachment.name}`}>
                    <Trash2 size={14} />
                  </button>
                </div>
                <p>{attachment.note}</p>
                {attachment.preview ? (
                  <details className="ai-chat-attachment-preview">
                    <summary>Prévia textual</summary>
                    <pre>{attachment.preview}</pre>
                  </details>
                ) : null}
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <div className="ai-chat-composer-toolbar">
        <div className="ai-chat-composer-actions">
          <button className="button ghost" type="button" onClick={openPicker} disabled={disabled}>
            <Paperclip size={14} />
            Anexar
          </button>
          <span className="ai-chat-composer-hint">{helperText}</span>
        </div>
        <div className="ai-chat-composer-stats">
          <span>{attachmentContextChars} chars de contexto</span>
          <span>{outgoingChars} chars no envio</span>
        </div>
      </div>

      <textarea
        ref={textareaRef}
        className="input ai-chat-composer-input"
        value={text}
        onChange={(event) => update(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            void submit();
          }
        }}
        placeholder={disabled ? "AI Chat indisponível no momento." : "Digite sua mensagem. Shift+Enter quebra linha."}
        rows={5}
        disabled={disabled}
      />

      <div className="ai-chat-composer-footer">
        <button className="button ghost" type="button" onClick={openPicker} disabled={disabled}>
          <Upload size={14} />
          Soltar/selecionar arquivos
        </button>
        <button className="button primary" type="button" onClick={() => void submit()} disabled={isSendDisabled}>
          <SendHorizonal size={14} />
          {isPreparingAttachments ? "Preparando..." : isSending ? "Enviando..." : "Enviar"}
        </button>
      </div>
    </div>
  );
}
