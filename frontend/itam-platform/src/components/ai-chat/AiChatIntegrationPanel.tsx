import { Bot, Files, Globe, MessageSquareText, ShieldAlert, Sparkles } from "lucide-react";

import type { AiChatMode, AiChatProviderHealth } from "@/lib/types";

const MODE_LABELS: Record<AiChatMode, string> = {
  general: "Geral",
  fix_text: "Corrigir texto",
  draft_ticket: "Abertura ITIL",
  update_ticket: "Atualização",
  resolution: "Solução aplicada",
  summarize: "Resumir",
  improve_tone: "Melhorar tom",
  service_macro: "Macro",
  asset_guidance: "Orientação de ativo",
};

type Props = {
  providerHealth: AiChatProviderHealth | null;
  selectedMode: AiChatMode;
  conversationCount: number;
  hiddenConversationCount: number;
  attachmentCount: number;
  attachmentContextChars: number;
  outgoingChars: number;
  isChatDisabled: boolean;
  attachmentsReady: boolean;
  providerLabel: string | null;
};

function statusTone(providerHealth: AiChatProviderHealth | null, isChatDisabled: boolean) {
  if (!providerHealth) {
    return "Neutro";
  }
  if (isChatDisabled || !providerHealth.enabled) {
    return "Inativo";
  }
  if (!providerHealth.configured) {
    return "Configuração pendente";
  }
  return "Operacional";
}

export function AiChatIntegrationPanel({
  providerHealth,
  selectedMode,
  conversationCount,
  hiddenConversationCount,
  attachmentCount,
  attachmentContextChars,
  outgoingChars,
  isChatDisabled,
  attachmentsReady,
  providerLabel,
}: Props) {
  return (
    <section className="ai-chat-panel card">
      <div className="ai-chat-panel-header">
        <div>
          <p className="ai-chat-panel-eyebrow">Painel de integração</p>
          <h2>Canal, contexto e segurança</h2>
        </div>
        <Sparkles aria-hidden="true" size={18} />
      </div>

      <div className="ai-chat-panel-section">
        <div className="ai-chat-panel-kpi">
          <Bot size={16} />
          <div>
            <span className="muted">Provider</span>
            <strong>{providerLabel ?? "Indisponível"}</strong>
          </div>
        </div>
        <div className="ai-chat-panel-metrics">
          <span>{statusTone(providerHealth, isChatDisabled)}</span>
          <span>{providerHealth?.status ?? "sem status"}</span>
        </div>
        <p className="ai-chat-panel-copy">
          O chat usa a API existente do backend para conversas e mensagens. Nenhuma ação operacional é executada a partir daqui.
        </p>
      </div>

      <div className="ai-chat-panel-section">
        <div className="ai-chat-panel-kpi">
          <MessageSquareText size={16} />
          <div>
            <span className="muted">Modo atual</span>
            <strong>{MODE_LABELS[selectedMode]}</strong>
          </div>
        </div>
        <div className="ai-chat-panel-metrics">
          <span>{conversationCount} conversas</span>
          <span>{hiddenConversationCount} ocultas localmente</span>
        </div>
      </div>

      <div className="ai-chat-panel-section">
        <div className="ai-chat-panel-kpi">
          <Files size={16} />
          <div>
            <span className="muted">Anexos locais</span>
            <strong>{attachmentCount} arquivo{attachmentCount === 1 ? "" : "s"}</strong>
          </div>
        </div>
        <div className="ai-chat-panel-metrics">
          <span>{attachmentContextChars} chars no contexto</span>
          <span>{outgoingChars} chars no envio</span>
        </div>
        <p className="ai-chat-panel-copy">
          Os anexos são convertidos em contexto textual no navegador antes do envio. Arquivos binários não são enviados como upload.
        </p>
        <div className="ai-chat-panel-callout">
          <Globe size={14} />
          <span>Sem endpoint de upload no backend. Esta integração é frontend-only e transparente.</span>
        </div>
        {!attachmentsReady ? (
          <div className="ai-chat-panel-callout warning">
            <ShieldAlert size={14} />
            <span>Preparando anexos para o contexto do chat.</span>
          </div>
        ) : null}
      </div>
    </section>
  );
}
