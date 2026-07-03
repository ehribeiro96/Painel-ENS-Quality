import { useMemo, useState } from "react";
import { Database, Search, SlidersHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { DonorPanelPageLayout } from "../components/DonorPanelPageLayout";
import { apoemaAssets, apoemaMetrics } from "../data";
import type { ApoemaAsset } from "../types";

export function AssetsPage() {
  const [query, setQuery] = useState("");
  const [selectedAsset, setSelectedAsset] = useState<ApoemaAsset>(apoemaAssets[0]);

  const filteredAssets = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
      return apoemaAssets;
    }
    return apoemaAssets.filter((asset) => [asset.name, asset.id, asset.category, asset.owner, asset.location, asset.status].join(" ").toLowerCase().includes(normalized));
  }, [query]);

  return (
    <DonorPanelPageLayout
      eyebrow="Inventário"
      title="Ativos e confiança operacional"
      description="Filtre, revise e priorize a base de ativos sem sair do shell donor-first."
      actions={
        <Button type="button" variant="outline" className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10">
          <SlidersHorizontal className="h-4 w-4" />
          Filtros avançados
        </Button>
      }
      stats={apoemaMetrics.slice(0, 4).map((metric) => ({
        label: metric.label,
        value: metric.value,
        detail: metric.hint,
      }))}
    >
      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_420px]">
        <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <label className="flex items-center gap-2 rounded-2xl border border-white/10 bg-slate-950/50 px-3 py-3 text-slate-300">
            <Search className="h-4 w-4 shrink-0 text-slate-500" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Buscar ativo, responsável ou local"
              className="w-full bg-transparent text-sm outline-none placeholder:text-slate-500"
            />
          </label>

          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {filteredAssets.map((asset) => (
              <button
                key={asset.id}
                type="button"
                onClick={() => setSelectedAsset(asset)}
                className={
                  selectedAsset.id === asset.id
                    ? "rounded-[24px] border border-cyan-300/20 bg-cyan-400/10 p-4 text-left"
                    : "rounded-[24px] border border-white/10 bg-slate-950/40 p-4 text-left transition-colors hover:bg-white/5"
                }
              >
                <div className="flex items-start justify-between gap-3">
                  <span className="text-sm font-medium text-slate-50">{asset.name}</span>
                  <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-slate-300">
                    {asset.status}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-400">
                  {asset.category} • {asset.owner}
                </p>
                <p className="mt-3 text-xs uppercase tracking-[0.18em] text-slate-500">{asset.location}</p>
              </button>
            ))}
          </div>
        </div>

        <aside className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Detalhe</p>
              <h3 className="mt-1 text-xl font-semibold text-slate-50">{selectedAsset.name}</h3>
              <p className="mt-1 text-sm text-slate-400">
                {selectedAsset.category} • {selectedAsset.owner}
              </p>
            </div>
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-100 ring-1 ring-cyan-300/20">
              <Database className="h-4 w-4" />
            </span>
          </div>

          <dl className="mt-5 grid gap-3 sm:grid-cols-2">
            <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
              <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">ID</dt>
              <dd className="mt-1 text-sm text-slate-100">{selectedAsset.id}</dd>
            </div>
            <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
              <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Local</dt>
              <dd className="mt-1 text-sm text-slate-100">{selectedAsset.location}</dd>
            </div>
            <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
              <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Último sinal</dt>
              <dd className="mt-1 text-sm text-slate-100">{selectedAsset.lastSeen}</dd>
            </div>
            <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
              <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Score</dt>
              <dd className="mt-1 text-sm text-slate-100">{selectedAsset.score}%</dd>
            </div>
          </dl>

          <div className="mt-5 rounded-[22px] border border-dashed border-white/15 bg-slate-950/35 p-4">
            <p className="text-sm font-medium text-slate-100">Ações sugeridas</p>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Criar macro, revisar última movimentação e validar conformidade antes de aplicar qualquer decisão.
            </p>
          </div>
        </aside>
      </section>
    </DonorPanelPageLayout>
  );
}
