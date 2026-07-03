import { Database, Globe2, ShieldCheck, Workflow } from "lucide-react";

import { DonorPanelPageLayout } from "../components/DonorPanelPageLayout";
import { apoemaIntegrations } from "../data";

const iconMap = [Database, Workflow, Globe2, ShieldCheck];

export function IntegrationsPage() {
  return (
    <DonorPanelPageLayout
      eyebrow="Integrações controladas"
      title="Adaptadores corporativos"
      description="Artifact Storage disponível no backend; demais integrações seguem com cobertura explícita e sem provider visual falso."
      stats={[
        { label: "Backend", value: "Online", detail: "Storage e contratos reais preservados." },
        { label: "MCP", value: "Mock-controlado", detail: "Sem provider externo na UI." },
        { label: "Cobertura", value: `${apoemaIntegrations.length}`, detail: "Adaptadores visíveis no painel." },
        { label: "Segurança", value: "Sem segredo", detail: "Nenhuma chave é exposta." },
      ]}
    >
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          { title: "Artifact Storage", description: "Disponível via backend /api/v1/artifacts, sem expor caminho interno no frontend.", status: "backend", icon: Database },
          { title: "RAG MCP", description: "Backend-owned com contrato visível; provider real não fica pendurado no shell.", status: "controlado", icon: Workflow },
          { title: "Designer API", description: "Geração assistida com fallback honesto e sem chave exposta no frontend.", status: "controlado", icon: Globe2 },
          { title: "Identity", description: "Perfil, permissões e contexto de operador com leitura rápida.", status: "backend", icon: ShieldCheck },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <article key={item.title} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
              <div className="flex items-start justify-between gap-3">
                <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-100 ring-1 ring-cyan-300/20">
                  <Icon className="h-4 w-4" />
                </span>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-slate-300">
                  {item.status}
                </span>
              </div>
              <h3 className="mt-4 text-lg font-semibold text-slate-50">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-400">{item.description}</p>
            </article>
          );
        })}
      </section>

      <section className="grid gap-4 xl:grid-cols-4">
        {apoemaIntegrations.map((integration, index) => {
          const Icon = iconMap[index % iconMap.length];
          const tone = integration.status === "live" ? "border-emerald-300/20 bg-emerald-400/10 text-emerald-100" : integration.status === "warning" ? "border-amber-300/20 bg-amber-400/10 text-amber-100" : "border-white/10 bg-white/5 text-slate-200";
          return (
            <article key={integration.name} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
              <div className="flex items-start justify-between gap-3">
                <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-100 ring-1 ring-cyan-300/20">
                  <Icon className="h-4 w-4" />
                </span>
                <span className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.18em] ${tone}`}>{integration.status}</span>
              </div>
              <h3 className="mt-4 text-lg font-semibold text-slate-50">{integration.name}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-400">{integration.description}</p>
              <dl className="mt-4 grid gap-3 sm:grid-cols-2">
                <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
                  <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Última sync</dt>
                  <dd className="mt-1 text-sm text-slate-100">{integration.lastSync}</dd>
                </div>
                <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
                  <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Cobertura</dt>
                  <dd className="mt-1 text-sm text-slate-100">{integration.coverage}</dd>
                </div>
              </dl>
            </article>
          );
        })}
      </section>
    </DonorPanelPageLayout>
  );
}
