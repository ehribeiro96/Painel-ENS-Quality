import { SendHorizonal } from "lucide-react";
import { useMemo } from "react";

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void | Promise<void>;
  disabled?: boolean;
  isSending?: boolean;
  placeholder?: string;
};

export function ChatComposer({
  value,
  onChange,
  onSubmit,
  disabled = false,
  isSending = false,
  placeholder = "Digite sua mensagem. Enter envia e Shift+Enter quebra linha.",
}: Props) {
  const sendDisabled = useMemo(() => disabled || isSending || !value.trim(), [disabled, isSending, value]);

  return (
    <div className={disabled ? "apoema-chat-composer is-disabled" : "apoema-chat-composer"}>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            if (!sendDisabled) {
              void onSubmit();
            }
          }
        }}
        placeholder={placeholder}
        rows={4}
        disabled={disabled}
        aria-busy={isSending}
      />
      <div className="apoema-chat-composer-actions">
        <span className="apoema-chat-composer-hint">Sem respostas progressivas, sem anexos e com envio explícito para o backend.</span>
        <button type="button" className="apoema-primary-button" onClick={() => void onSubmit()} disabled={sendDisabled}>
          <SendHorizonal size={16} />
          {isSending ? "Enviando..." : "Enviar"}
        </button>
      </div>
    </div>
  );
}
