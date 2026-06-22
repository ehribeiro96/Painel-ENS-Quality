import { Database, Globe2, ShieldCheck, Workflow } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { apoemaIntegrations } from "../data";

const iconMap = [Database, Workflow, Globe2, ShieldCheck];

export function IntegrationsPage() {
  return (
    <div className="apoema-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="success">Integrações mockadas</StatusPill>
          <h1>Adaptadores corporativos com visão clara de cobertura.</h1>
          <p>Monitore conectores, janelas de sincronização e qualidade de integração.</p>
        </div>
      </section>

      <section className="apoema-integration-grid">
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
