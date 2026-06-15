import { useEffect, useRef, useState } from "react";

type Props = {
  disabled?: boolean;
  value?: string;
  onValueChange?: (value: string) => void;
  onSend: (content: string) => Promise<void> | void;
  isSending?: boolean;
};

export function ChatComposer({ disabled, value, onValueChange, onSend, isSending }: Props) {
  const [internalValue, setInternalValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
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
    if (!content || disabled) {
      return;
    }
    await onSend(content);
  }

  const isSendDisabled = Boolean(disabled || !text.trim());

  return (
    <div className={disabled ? "ai-chat-composer disabled" : "ai-chat-composer"}>
      <textarea
        ref={textareaRef}
        className="input"
        value={text}
        onChange={(event) => update(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            void submit();
          }
        }}
        placeholder={disabled ? "AI Chat indisponível no momento." : "Digite sua mensagem. Shift+Enter quebra linha."}
        rows={4}
        disabled={disabled}
      />
      <button className="button primary" type="button" onClick={() => void submit()} disabled={isSendDisabled}>
        {isSending ? "Enviando..." : "Enviar"}
      </button>
    </div>
  );
}
