import { Mic, Send } from "lucide-react";

export function ChatComposer({
  value,
  onChange,
  onSubmit,
  disabled,
  placeholder = "Digite sua pergunta..."
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  placeholder?: string;
}) {
  return (
    <div className="apoema-chat-composer">
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        rows={3}
      />
      <div className="apoema-chat-composer-actions">
        <button type="button" className="apoema-ghost-button">
          <Mic size={16} />
          Ditado
        </button>
        <button type="button" className="apoema-primary-button" onClick={onSubmit} disabled={disabled}>
          <Send size={16} />
          Enviar
        </button>
      </div>
    </div>
  );
}
