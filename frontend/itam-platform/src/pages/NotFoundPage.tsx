import { Link } from "react-router-dom";
import { ArrowLeft, Home, Radar } from "lucide-react";

import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44Surface } from "@/components/base44/Base44Surface";

export function NotFoundPage() {
  return (
    <main className="base44-notfound-shell">
      <Base44Surface className="base44-notfound-card">
        <Base44PageHeader
          eyebrow="404"
          title="Página não encontrada"
          description="A rota solicitada não existe no console operacional."
        />
        <Base44EmptyState
          title="Nada por aqui"
          description="Volte ao dashboard para continuar navegando no painel operacional."
          action={(
            <div className="empty-state-actions">
              <Link className="button" to="/">
                <Home size={16} aria-hidden="true" />
                <span>Voltar ao dashboard</span>
              </Link>
              <Link className="button secondary" to="/assets">
                <ArrowLeft size={16} aria-hidden="true" />
                <span>Ir para inventário</span>
              </Link>
            </div>
          )}
          icon={Radar}
        />
      </Base44Surface>
    </main>
  );
}
