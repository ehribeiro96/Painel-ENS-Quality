import { Link } from "react-router-dom";
import { ArrowRight, Clock3, Sparkles, WandSparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { DonorPanelPageLayout } from "../components/DonorPanelPageLayout";
import { apoemaActivities, apoemaCommands, apoemaMetrics, apoemaQuickIdeas } from "../data";

export function DashboardPage() {
  return (
    <DonorPanelPageLayout
      eyebrow="Centro de operações"
      title="Painel operacional"
      description="Inventário, macros, atendimento e auditoria em uma visão única e direta, com shell donor-first e contrastes consistentes."
      actions={
        <>
          <Button asChild className="rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300">
            <Link to="/apoema/chat">
              <Sparkles className="h-4 w-4" />
              Abrir chat
            </Link>
          </Button>
          <Button asChild variant="outline" className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10">
            <Link to="/apoema/assets">
              <ArrowRight className="h-4 w-4" />
              Ver ativos
            </Link>
          </Button>
        </>
      }
      stats={apoemaMetrics.slice(0, 4).map((metric) => ({
        label: metric.label,
        value: metric.value,
        detail: metric.hint,
      }))}
    >
      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(0,0.9fr)]">
        <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Atalhos operacionais</p>
              <h3 className="mt-1 text-lg font-semibold text-slate-50">Ações rápidas</h3>
            </div>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">Fluxo ativo</span>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            {apoemaCommands.map((command) => (
              <article key={command.title} className="rounded-[22px] border border-white/10 bg-slate-950/40 p-4">
                <p className="text-sm font-medium text-slate-100">{command.title}</p>
                <p className="mt-2 text-sm leading-6 text-slate-400">{command.description}</p>
                <button type="button" className="mt-4 inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-cyan-300">
                  <WandSparkles className="h-4 w-4" />
                  {command.action}
                </button>
              </article>
            ))}
          </div>
        </div>

        <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Sinais recentes</p>
              <h3 className="mt-1 text-lg font-semibold text-slate-50">Linha do tempo</h3>
            </div>
            <Clock3 className="h-4 w-4 text-cyan-100" />
          </div>
          <div className="space-y-3">
            {apoemaActivities.map((activity) => (
              <article key={activity.title} className="rounded-[22px] border border-white/10 bg-slate-950/40 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.22em] text-slate-500">{activity.time}</p>
                    <h4 className="mt-1 text-sm font-medium text-slate-50">{activity.title}</h4>
                  </div>
                  <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-slate-400">
                    {activity.tone}
                  </span>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-400">{activity.detail}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Ideias rápidas</p>
            <h3 className="mt-1 text-lg font-semibold text-slate-50">Use uma sugestão para começar</h3>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {apoemaQuickIdeas.map((idea) => (
            <article key={idea} className="rounded-[22px] border border-white/10 bg-slate-950/40 p-4">
              <p className="text-sm font-medium text-slate-100">{idea}</p>
              <p className="mt-2 text-sm leading-6 text-slate-400">Prompt operacional para acelerar a análise e ação.</p>
            </article>
          ))}
        </div>
      </section>
    </DonorPanelPageLayout>
  );
}
