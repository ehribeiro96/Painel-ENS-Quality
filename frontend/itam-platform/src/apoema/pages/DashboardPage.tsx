import { CommandCard } from "../components/CommandCard";
import { EmptyState } from "../components/EmptyState";
import { MetricCard } from "../components/MetricCard";
import { StatusPill } from "../components/StatusPill";
import { apoemaActivities, apoemaCommands, apoemaMetrics, apoemaQuickIdeas } from "../data";

export function DashboardPage() {
  return (
    <div className="apoema-page">
      <section className="apoema-hero">
        <div className="apoema-hero-copy">
          <StatusPill tone="success">Centro de operações</StatusPill>
          <h1>Operações que impulsionam valor com IA e inventário unificado.</h1>
          <p>
            Apoema é a camada corporativa para N2, inventário, movimentos, macros ITIL, auditoria
            e suporte inteligente. Tudo com uma experiência visual premium.
          </p>
          <div className="apoema-hero-actions">
            <button type="button" className="apoema-primary-button">Abrir painel operacional</button>
            <button type="button" className="apoema-secondary-button">Ver integrações</button>
          </div>
        </div>
        <div className="apoema-hero-panel">
          <div className="apoema-hero-panel-top">
            <strong>Janela operacional</strong>
            <span>Últimos 30 dias</span>
          </div>
          <div className="apoema-hero-card-grid">
            {apoemaMetrics.slice(0, 3).map((metric) => (
              <MetricCard key={metric.label} metric={metric} />
            ))}
          </div>
        </div>
      </section>

      <section className="apoema-section-grid">
        <div className="apoema-panel">
          <div className="apoema-section-head">
            <h2>Atalhos operacionais</h2>
            <span>Mocked action lane</span>
          </div>
          <div className="apoema-command-grid">
            {apoemaCommands.map((command) => (
              <CommandCard key={command.title} command={command} />
            ))}
          </div>
        </div>

        <div className="apoema-panel">
          <div className="apoema-section-head">
            <h2>Sinais recentes</h2>
            <span>Telemetry feed</span>
          </div>
          <div className="apoema-timeline">
            {apoemaActivities.map((activity) => (
              <article key={activity.title} className={`apoema-timeline-item tone-${activity.tone}`}>
                <time>{activity.time}</time>
                <div>
                  <strong>{activity.title}</strong>
                  <p>{activity.detail}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="apoema-panel">
        <div className="apoema-section-head">
          <h2>Ideias rápidas</h2>
          <span>Copie uma sugestão para o chat</span>
        </div>
        <div className="apoema-idea-grid">
          {apoemaQuickIdeas.map((idea) => (
            <EmptyState key={idea} title={idea} description="Prompt operacional para acelerar a análise e ação." />
          ))}
        </div>
      </section>
    </div>
  );
}
