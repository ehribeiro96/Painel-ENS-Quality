import { CheckCircle2, LayoutGrid, Shield, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { DonorPanelPageLayout } from "../components/DonorPanelPageLayout";
import { apoemaPreferences } from "../data";
import { useThemeMode } from "../hooks/useThemeMode";

export function SettingsPage() {
  const theme = useThemeMode();

  return (
    <DonorPanelPageLayout
      eyebrow="Configurações"
      title="Tema, segurança e densidade"
      description="Preferências visuais e proteções operacionais alinhadas ao shell donor-first."
      actions={
        <div className="flex flex-wrap gap-2">
          {(["light", "dark", "auto"] as const).map((mode) => (
            <Button
              key={mode}
              type="button"
              variant={theme.mode === mode ? "default" : "outline"}
              className={
                theme.mode === mode
                  ? "rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300"
                  : "rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10"
              }
              onClick={() => theme.setMode(mode)}
            >
              {mode === "light" ? "Claro" : mode === "dark" ? "Escuro" : "Sistema"}
            </Button>
          ))}
        </div>
      }
      stats={[
        { label: "Preferências", value: apoemaPreferences.length, detail: "Opções visuais e de segurança ativas." },
        { label: "Tema atual", value: theme.mode, detail: "Persistido no navegador." },
        { label: "Proteções", value: "3", detail: "Bloqueios e alertas de contexto sensível." },
        { label: "Shell", value: "Donor-first", detail: "Sidebar retrátil e sem scrollbar visível." },
      ]}
    >
      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_420px]">
        <article className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Preferências</p>
              <h3 className="mt-1 text-lg font-semibold text-slate-50">Perfil visual</h3>
            </div>
            <LayoutGrid className="h-4 w-4 text-cyan-100" />
          </div>
          <div className="grid gap-3">
            {apoemaPreferences.map((pref) => (
              <article key={pref.label} className="rounded-[22px] border border-white/10 bg-slate-950/40 p-4">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-100">
                    {pref.enabled ? <CheckCircle2 className="h-4 w-4" /> : <LayoutGrid className="h-4 w-4" />}
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-slate-50">{pref.label}</h4>
                    <p className="mt-1 text-sm leading-6 text-slate-400">{pref.description}</p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </article>

        <article className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Segurança</p>
              <h3 className="mt-1 text-lg font-semibold text-slate-50">Proteções operacionais</h3>
            </div>
            <Shield className="h-4 w-4 text-cyan-100" />
          </div>
          <div className="space-y-3">
            <div className="rounded-[22px] border border-white/10 bg-slate-950/40 p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-100">
                  <Shield className="h-4 w-4" />
                </div>
                <div>
                  <strong className="block text-sm font-medium text-slate-50">Proteção de contexto</strong>
                  <p className="text-sm leading-6 text-slate-400">Arquivos sensíveis e credenciais são destacados antes de qualquer ação.</p>
                </div>
              </div>
            </div>
            <div className="rounded-[22px] border border-white/10 bg-slate-950/40 p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-100">
                  <Sparkles className="h-4 w-4" />
                </div>
                <div>
                  <strong className="block text-sm font-medium text-slate-50">Assistência centrada em IA</strong>
                  <p className="text-sm leading-6 text-slate-400">O fluxo prioriza resumo, recomendação e execução segura no caminho real.</p>
                </div>
              </div>
            </div>
          </div>
          <p className="mt-4 rounded-[22px] border border-white/10 bg-white/5 p-4 text-sm leading-6 text-slate-300">
            Nenhum token, senha, cookie ou header é renderizado nesta interface.
          </p>
        </article>
      </section>
    </DonorPanelPageLayout>
  );
}
