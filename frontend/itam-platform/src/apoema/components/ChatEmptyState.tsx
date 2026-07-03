import { Bot, MessageSquarePlus, Sparkles } from "lucide-react";
import { StatusPill } from "./StatusPill";

export type ChatPromptSuggestion = {
  label: string;
  prompt: string;
};

type Props = {
  onNewConversation: () => void | Promise<void>;
  onPickSuggestion: (prompt: string) => void;
  suggestions: ChatPromptSuggestion[];
};

export function ChatEmptyState({ onNewConversation, onPickSuggestion, suggestions }: Props) {
  return (
    <section className="apoema-chat-empty-state" aria-label="Estado vazio do chat">
      <StatusPill tone="info">
        <Sparkles size={14} />
        Pronto para operar
      </StatusPill>
      <strong>Pronto para ajudar com inventário, ativos e macros.</strong>
      <p>Envie uma pergunta ou escolha uma sugestão para iniciar uma conversa.</p>

      <div className="apoema-chat-empty-actions">
        <button className="apoema-primary-button" type="button" onClick={() => void onNewConversation()}>
          <MessageSquarePlus size={14} />
          Nova conversa
        </button>
        <button className="apoema-secondary-button" type="button" onClick={() => onPickSuggestion(suggestions[0]?.prompt ?? "")} disabled={!suggestions.length}>
          <Bot size={14} />
          Usar sugestão
        </button>
      </div>

      {suggestions.length > 0 ? (
        <div className="apoema-chat-empty-suggestions" aria-label="Sugestões rápidas">
          {suggestions.map((suggestion, index) => (
            <button key={`${suggestion.label}-${index}`} className="apoema-chat-suggestion" type="button" onClick={() => onPickSuggestion(suggestion.prompt)}>
              {suggestion.label}
            </button>
          ))}
        </div>
      ) : null}
    </section>
  );
}
