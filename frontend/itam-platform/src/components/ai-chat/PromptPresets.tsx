import type { AiChatMode } from "@/lib/types";

export type PromptPreset = {
  label: string;
  mode: AiChatMode;
  text: string;
};

const presets: PromptPreset[] = [
  { label: "Geral", mode: "general", text: "Ajude com o texto abaixo de forma objetiva:\n\n" },
  { label: "Corrigir texto", mode: "fix_text", text: "Corrija o texto abaixo mantendo o sentido:\n\n" },
  { label: "Abertura ITIL", mode: "draft_ticket", text: "Gere uma abertura ITIL estruturada para:\n\n" },
  { label: "Atualização", mode: "update_ticket", text: "Gere uma atualização de chamado para:\n\n" },
  { label: "Solução aplicada", mode: "resolution", text: "Gere um texto de solução aplicada para:\n\n" },
  { label: "Resumir", mode: "summarize", text: "Resuma o atendimento abaixo em tópicos objetivos:\n\n" },
  { label: "Melhorar tom", mode: "improve_tone", text: "Melhore o tom da mensagem abaixo, mantendo cordialidade e objetividade:\n\n" },
  { label: "Macro", mode: "service_macro", text: "Gere uma macro cordial e direta para o atendimento abaixo:\n\n" },
  { label: "Orientação de ativo", mode: "asset_guidance", text: "Gere uma orientação segura de inventário/movimentação para:\n\n" }
];

type Props = {
  selectedMode?: AiChatMode;
  onSelect: (preset: PromptPreset) => void;
};

export function PromptPresets({ selectedMode = "general", onSelect }: Props) {
  return (
    <div className="ai-chat-presets" aria-label="Modos textuais do IA Chat">
      {presets.map((preset) => (
        <button
          className={preset.mode === selectedMode ? "button ghost active" : "button ghost"}
          key={preset.mode}
          type="button"
          onClick={() => onSelect(preset)}
          aria-pressed={preset.mode === selectedMode}
        >
          {preset.label}
        </button>
      ))}
    </div>
  );
}
