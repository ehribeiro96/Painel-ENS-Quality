import { Database, Globe2, ShieldCheck, Workflow } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { apoemaIntegrations } from "../data";

const iconMap = [Database, Workflow, Globe2, ShieldCheck];

export function IntegrationsPage() {
  return (
    <div className="apoema-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="success">Integrações controladas</StatusPill>
          <h1>Adaptadores corporativos com cobertura clara e leitura rápida.</h1>
          <p>Artifact Storage disponível no backend; RAG MCP e Designer API seguem como mocks determinísticos. Providers reais permanecem desativados.</p>
        </div>
      </section>

      <section className="apoema-integration-grid">
        <article className="apoema-integration-card">
          <div className="apoema-integration-head">
            <span className="apoema-integration-icon"><Database size={18} /></span>
            <StatusPill tone="success">backend</StatusPill>
          </div>
          <strong>Artifact Storage</strong>
          <p>Disponível via backend /api/v1/artifacts, sem expor caminho interno no frontend.</p>
        </article>
        <article className="apoema-integration-card">
          <div className="apoema-integration-head">
            <span className="apoema-integration-icon"><Workflow size={18} /></span>
            <StatusPill tone="warning">mock</StatusPill>
          </div>
          <strong>RAG MCP</strong>
          <p>Mock determinístico backend-owned; MCP real, vector store e provider real desativados.</p>
        </article>
        <article className="apoema-integration-card">
          <div className="apoema-integration-head">
            <span className="apoema-integration-icon"><ShieldCheck size={18} /></span>
            <StatusPill tone="warning">mock</StatusPill>
          </div>
          <strong>Designer API</strong>
          <p>Mock determinístico para jobs; sem geração real de imagem e sem chave de provider no frontend.</p>
        </article>
        {apoemaIntegrations.map((integration, index) => {
          const Icon = iconMap[index % iconMap.length];
          return (
            <article key={integration.name} className="apoema-integration-card">
              <div className="apoema-integration-head">
                <span className="apoema-integration-icon">
                  <Icon size={18} />
                </span>
                <StatusPill tone={integration.status === "live" ? "success" : integration.status === "warning" ? "warning" : "neutral"}>
                  {integration.status}
                </StatusPill>
              </div>
              <strong>{integration.name}</strong>
              <p>{integration.description}</p>
              <dl>
                <div>
                  <dt>Última sync</dt>
                  <dd>{integration.lastSync}</dd>
                </div>
                <div>
                  <dt>Cobertura</dt>
                  <dd>{integration.coverage}</dd>
                </div>
              </dl>
            </article>
          );
        })}
      </section>
    </div>
  );
}
