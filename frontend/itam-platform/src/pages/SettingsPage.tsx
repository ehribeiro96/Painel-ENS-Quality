import { CheckCircle2, ShieldCheck, Wrench } from "lucide-react";

import { Base44InfoGrid } from "@/components/base44/Base44InfoGrid";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44SettingsSection } from "@/components/base44/Base44SettingsSection";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";

export function SettingsPage() {
  return (
    <div className="base44-settings-page">
      <Base44PageHeader
        eyebrow="Configurações do sistema"
        title="Configurações"
        description="Preferências operacionais, integrações futuras e perímetro de segurança apresentados com a mesma linguagem visual Base44, sem alterar os contratos reais da aplicação."
        actions={<Base44StatusBadge status="auditavel">Somente visual</Base44StatusBadge>}
      />

      <section className="grid base44-settings-summary-grid" aria-label="Resumo de configurações">
        <Base44InfoGrid
          columns={4}
          title="Contexto atual"
          items={[
            { label: "Autenticação", value: "Real", hint: "Permissões e sessão continuam vindas da camada existente." },
            { label: "Integrações", value: "Expostas", hint: "Lansweeper e futuras integrações permanecem descritivas." },
            { label: "Segurança", value: "Preservada", hint: "Nenhum segredo ou token é exibido nesta tela." },
            { label: "Backend", value: "Sem alteração", hint: "A página permanece estritamente visual." },
          ]}
        />
      </section>

      <section className="grid base44-settings-sections-grid">
        <Base44SettingsSection
          eyebrow="Geral"
          title="Preferências operacionais"
          description="Notificações, comportamento padrão e sinais de apoio ao fluxo real da plataforma."
          status="Operacional"
          actions={<Base44StatusBadge status="success">Ativo</Base44StatusBadge>}
        >
          <div className="base44-settings-list">
            <article>
              <div>
                <p className="base44-settings-item-title">Notificações por email</p>
                <p className="base44-settings-item-description">Receber alertas de inconsistências e mudanças relevantes.</p>
              </div>
              <Base44StatusBadge status="leitura">Mantido</Base44StatusBadge>
            </article>
            <article>
              <div>
                <p className="base44-settings-item-title">Auto-detecção de inconsistências</p>
                <p className="base44-settings-item-description">Verificação automática após importações e operações críticas.</p>
              </div>
              <Base44StatusBadge status="auditavel">Auditável</Base44StatusBadge>
            </article>
            <article>
              <div>
                <p className="base44-settings-item-title">Acompanhamento de auditoria</p>
                <p className="base44-settings-item-description">Auditoria, rastreabilidade e revisão humana seguem visíveis na UI.</p>
              </div>
              <Base44StatusBadge status="auditavel">Ativo</Base44StatusBadge>
            </article>
          </div>
        </Base44SettingsSection>

        <Base44SettingsSection
          eyebrow="Integrações"
          title="Lansweeper e serviços futuros"
          description="A tela expõe o que a UI já conhece, sem revelar credenciais, tokens ou qualquer valor sensível."
          status="Integrações"
          actions={<Base44StatusBadge status="warning">Sem segredo</Base44StatusBadge>}
        >
          <div className="base44-settings-list base44-settings-integrations">
            <article>
              <div className="base44-settings-icon"><Wrench size={16} aria-hidden /></div>
              <div>
                <p className="base44-settings-item-title">Lansweeper API</p>
                <p className="base44-settings-item-description">Preparado para URL, sincronização incremental, retry e timeout.</p>
              </div>
            </article>
            <article>
              <div className="base44-settings-icon"><ShieldCheck size={16} aria-hidden /></div>
              <div>
                <p className="base44-settings-item-title">Microsoft Entra ID</p>
                <p className="base44-settings-item-description">Preparado para tenant, client ID e escopos via variáveis seguras.</p>
              </div>
            </article>
            <article>
              <div className="base44-settings-icon"><CheckCircle2 size={16} aria-hidden /></div>
              <div>
                <p className="base44-settings-item-title">Próximas integrações</p>
                <p className="base44-settings-item-description">Espaço visual reservado para integrações futuras sem mock funcional.</p>
              </div>
            </article>
          </div>
        </Base44SettingsSection>

        <Base44SettingsSection
          eyebrow="Permissões"
          title="RBAC e perímetro de acesso"
          description="Papéis, leitura e escrita seguem determinados pela camada real de autorização do projeto."
          status="RBAC"
          actions={<Base44StatusBadge status="auditavel">Preservado</Base44StatusBadge>}
        >
          <div className="base44-settings-list">
            <article>
              <div>
                <p className="base44-settings-item-title">Papéis administrativos</p>
                <p className="base44-settings-item-description">Administradores continuam com acesso a configurações e operações sensíveis.</p>
              </div>
              <Base44StatusBadge status="auditavel">ADMIN</Base44StatusBadge>
            </article>
            <article>
              <div>
                <p className="base44-settings-item-title">Leitura controlada</p>
                <p className="base44-settings-item-description">Perfis limitados seguem sem revelar dados sensíveis ou opções inexistentes.</p>
              </div>
              <Base44StatusBadge status="leitura">RBAC real</Base44StatusBadge>
            </article>
            <article>
              <div>
                <p className="base44-settings-item-title">Segurança visual</p>
                <p className="base44-settings-item-description">Nenhum token, senha, cookie ou header é renderizado nesta interface.</p>
              </div>
              <Base44StatusBadge status="warning">Seguro</Base44StatusBadge>
            </article>
          </div>
        </Base44SettingsSection>
      </section>
    </div>
  );
}
