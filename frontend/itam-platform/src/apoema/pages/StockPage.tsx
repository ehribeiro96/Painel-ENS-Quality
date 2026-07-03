import { useEffect, useMemo, useState } from "react";

import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { DonorChip } from "../components/DonorForm";
import { DonorPanelPageLayout } from "../components/DonorPanelPageLayout";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const stockLabels = [
  "STOCK",
  "RESERVED",
  "CONFIG_PENDING",
  "MAINTENANCE",
  "DEFECTIVE",
  "DISCARDED",
];

export function StockPage() {
  const { token } = useAuth();
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }

    setLoading(true);
    api
      .assetsByStatus(token)
      .then((data) => {
        setCounts(Object.fromEntries(data.map((item) => [item.status, item.count])));
        setError(null);
      })
      .catch(() => setError("Não foi possível carregar os indicadores de estoque."))
      .finally(() => setLoading(false));
  }, [token]);

  const metrics = useMemo(
    () =>
      stockLabels.map((label) => ({
        label,
        value: counts[label] ?? 0,
        detail: counts[label] ? `Itens em ${label.toLowerCase().replaceAll("_", " ")}` : "Sem itens nessa categoria.",
      })),
    [counts],
  );
  const total = metrics.reduce((sum, item) => sum + Number(item.value), 0);

  return (
    <DonorPanelPageLayout
      eyebrow="Apoema Estoque"
      title="Estoque"
      description="Visão operacional de disponibilidade, reservas, manutenção e descarte, usando os totais reais expostos pela API de ativos por status."
      actions={<DonorChip>{loading ? "Atualizando" : "API real"}</DonorChip>}
      stats={[
        { label: "Total", value: total, detail: "Itens somados a partir dos status." },
        { label: "Em estoque", value: counts.STOCK ?? 0, detail: "Disponíveis para operação." },
        { label: "Reservados", value: counts.RESERVED ?? 0, detail: "Aguardando alocação." },
        { label: "Em manutenção", value: counts.MAINTENANCE ?? 0, detail: "Itens sob revisão." },
      ]}
    >
      {error ? (
        <Alert tone="danger">
          <strong>{error}</strong>
          <p>Confirme sua sessão e tente novamente quando a API estiver disponível.</p>
        </Alert>
      ) : null}
      {loading ? <LoadingBlock label="Carregando indicadores de estoque..." /> : null}

      <section className="rounded-[26px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_50px_-26px_rgba(0,0,0,0.8)]">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Distribuição operacional</p>
            <h2 className="mt-2 text-lg font-semibold text-slate-50">Resumo do estoque</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">Os cartões abaixo usam os totais reais retornados pela API de estoque.</p>
          </div>
          <DonorChip>{total} total</DonorChip>
        </div>

        {total === 0 ? (
          <div className="mt-5 rounded-[22px] border border-dashed border-white/15 bg-slate-950/35 p-5 text-sm text-slate-400">
            Nenhum indicador disponível no momento.
          </div>
        ) : (
          <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {metrics.map((metric) => (
              <article key={metric.label} className="rounded-[22px] border border-white/10 bg-slate-950/45 p-4">
                <p className="text-xs uppercase tracking-[0.22em] text-slate-500">{metric.label}</p>
                <p className="mt-2 text-2xl font-semibold text-slate-50">{metric.value}</p>
                <p className="mt-2 text-sm leading-6 text-slate-300">{metric.detail}</p>
              </article>
            ))}
          </div>
        )}
      </section>
    </DonorPanelPageLayout>
  );
}
