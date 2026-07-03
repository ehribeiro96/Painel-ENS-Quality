import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";

export function DonorNotFound() {
  return (
    <div className="grid min-h-[60vh] place-items-center">
      <section className="max-w-xl rounded-[28px] border border-white/10 bg-white/[0.04] p-8 text-center shadow-[0_20px_60px_-28px_rgba(0,0,0,0.8)]">
        <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Rota não encontrada</p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-50">A página solicitada não existe no shell atual.</h2>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          Use a navegação lateral para voltar para o chat ou para uma página operacional do Apoema.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Button asChild className="rounded-2xl bg-cyan-400 px-5 text-slate-950 hover:bg-cyan-300">
            <Link to="/apoema/chat">Ir para o chat</Link>
          </Button>
          <Button asChild variant="outline" className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10">
            <Link to="/apoema/dashboard">Abrir dashboard</Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
