import { useMemo, useState } from "react";
import { DataTable } from "../components/DataTable";
import { EmptyState } from "../components/EmptyState";
import { MetricCard } from "../components/MetricCard";
import { StatusPill } from "../components/StatusPill";
import { apoemaAssets, apoemaMetrics } from "../data";
import type { ApoemaAsset } from "../types";
import { Search, SlidersHorizontal } from "lucide-react";

export function AssetsPage() {
  const [query, setQuery] = useState("");
  const [selectedAsset, setSelectedAsset] = useState<ApoemaAsset>(apoemaAssets[0]);

  const filteredAssets = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
      return apoemaAssets;
    }

    return apoemaAssets.filter((asset) =>
      [asset.name, asset.id, asset.category, asset.owner, asset.location, asset.status]
        .join(" ")
        .toLowerCase()
        .includes(normalized)
    );
  }, [query]);

  return (
    <div className="apoema-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="info">Inventário</StatusPill>
          <h1>Ativos, score de confiança e visibilidade operacional.</h1>
          <p>Filtre, revise e priorize a base de ativos sem sair do console.</p>
        </div>
        <div className="apoema-mini-stats">
          {apoemaMetrics.map((metric) => (
            <MetricCard key={metric.label} metric={metric} />
          ))}
        </div>
      </section>

      <section className="apoema-panel">
        <div className="apoema-filter-bar">
          <label className="apoema-search">
            <Search size={16} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar ativo, responsável ou local" />
          </label>
          <button type="button" className="apoema-secondary-button">
            <SlidersHorizontal size={16} />
            Filtros avançados
          </button>
        </div>

        <div className="apoema-assets-layout">
          <DataTable rows={filteredAssets} selectedId={selectedAsset.id} onSelect={setSelectedAsset} />

          <aside className="apoema-detail-card">
            <StatusPill tone={selectedAsset.status === "healthy" ? "success" : selectedAsset.status === "review" ? "warning" : "neutral"}>
              {selectedAsset.status}
            </StatusPill>
            <h2>{selectedAsset.name}</h2>
            <p>{selectedAsset.category} • {selectedAsset.owner}</p>
            <dl className="apoema-detail-grid">
              <div>
                <dt>ID</dt>
                <dd>{selectedAsset.id}</dd>
              </div>
              <div>
                <dt>Local</dt>
                <dd>{selectedAsset.location}</dd>
              </div>
              <div>
                <dt>Último sinal</dt>
                <dd>{selectedAsset.lastSeen}</dd>
              </div>
              <div>
                <dt>Score</dt>
                <dd>{selectedAsset.score}%</dd>
              </div>
            </dl>
            <EmptyState
              title="Ações sugeridas"
              description="Criar macro, revisar última movimentação e validar conformidade antes de aplicar qualquer decisão."
            />
          </aside>
        </div>
      </section>
    </div>
  );
}
