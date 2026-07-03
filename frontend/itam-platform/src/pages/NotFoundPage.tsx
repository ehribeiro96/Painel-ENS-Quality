import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Bot, Home } from "lucide-react";

export function NotFoundPage() {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.18),transparent_28%),radial-gradient(circle_at_80%_0%,rgba(34,211,238,0.12),transparent_26%),linear-gradient(180deg,#07111f_0%,#09131f_100%)] p-4">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/4 top-1/4 h-96 w-96 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-sky-400/10 blur-3xl" />
      </div>

      <div className="z-10 w-full max-w-2xl rounded-[28px] border border-white/10 bg-slate-950/70 p-8 text-center shadow-[0_24px_80px_-24px_rgba(0,0,0,0.8)] backdrop-blur-xl">
        <div className="flex flex-col items-center gap-4">
          <div className="flex h-20 w-20 items-center justify-center rounded-[24px] border border-white/10 bg-white/5 shadow-[0_18px_50px_-24px_rgba(0,0,0,0.85)]">
            <img src="/logo.svg" alt="Apoema" className="h-12 w-12" />
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.4em] text-cyan-200/70">Rota não encontrada</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-50">A página solicitada não existe no shell atual.</h1>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Use a navegação lateral para voltar para o chat ou para uma página operacional do Apoema.
            </p>
          </div>
        </div>

        <section className="mt-8 grid gap-4 md:grid-cols-2">
          <article className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5 text-left shadow-[0_20px_60px_-28px_rgba(0,0,0,0.8)]">
            <div className="flex items-center gap-3">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-cyan-400/10 text-cyan-100">
                <Bot size={16} aria-hidden="true" />
              </span>
              <div>
                <strong className="block text-base text-slate-50">Chat principal</strong>
                <p className="text-sm text-slate-300">O fluxo principal continua em /apoema/chat.</p>
              </div>
            </div>
          </article>

          <article className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5 text-left shadow-[0_20px_60px_-28px_rgba(0,0,0,0.8)]">
            <div className="flex items-center gap-3">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-sky-400/10 text-sky-100">
                <Home size={16} aria-hidden="true" />
              </span>
              <div>
                <strong className="block text-base text-slate-50">Painel Apoema</strong>
                <p className="text-sm text-slate-300">Auth e RBAC seguem no shell donor-first, sem shell legado.</p>
              </div>
            </div>
          </article>
        </section>

        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          <ButtonLink to="/apoema/chat" icon={<Bot size={16} aria-hidden="true" />} label="Abrir chat" />
          <ButtonLink to="/apoema" icon={<Home size={16} aria-hidden="true" />} label="Ir para o painel" />
          <ButtonLink to="/" icon={<ArrowLeft size={16} aria-hidden="true" />} label="Voltar ao início" />
        </div>
      </div>
    </main>
  );
}

function ButtonLink({ to, icon, label }: { to: string; icon: ReactNode; label: string }) {
  return (
    <Link
      className="inline-flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-slate-100 shadow-[0_16px_40px_-24px_rgba(0,0,0,0.8)] transition-colors hover:border-cyan-300/30 hover:bg-cyan-400/10"
      to={to}
    >
      {icon}
      <span>{label}</span>
    </Link>
  );
}
