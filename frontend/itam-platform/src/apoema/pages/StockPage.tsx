import { useEffect, useMemo, useState } from "react";

import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44MetricCard } from "@/components/base44/Base44MetricCard";
import { Base44OperationalGrid } from "@/components/base44/Base44OperationalGrid";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const stockLabels = [
  "STOCK",
  "RESERVED",
  "CONFIG_PENDING",
  "MAINTENANCE",
  "DEFECTIVE",
  "DISCARDED"
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

  const labels = useMemo(() => stockLabels.map((label) => [label, counts[label] ?? 0] as const), [counts]);
  const total = labels.reduce((sum, [, value]) => sum + value, 0);

  return (
    <div className="base44-operation-page">
      <Base44PageHeader
        eyebrow="Apoema Estoque"
        title="Estoque"
        description="Visão operacional de disponibilidade, reservas, manutenção e descarte, usando os totais reais expostos pela API de ativos por status."
        actions={
          <Base44StatusBadge status={loading ? "warning" : "auditavel"}>{loading ? "Atualizando" : "API real"}</Base44StatusBadge>
        }
      />

      {error ? (
        <Alert tone="danger">
          <strong>{error}</strong>
          <p>Confirme sua sessão e tente novamente quando a API estiver disponível.</p>
        </Alert>
      ) : null}
      {loading ? <LoadingBlock label="Carregando indicadores de estoque..." /> : null}

      <Base44OperationalGrid
        title="Distribuição operacional"
        description="Os cartões abaixo usam os totais reais retornados pela API de estoque."
        columns={3}
        items={labels.map(([label, value]) => ({
          title: label,
          value,
          description: `Total atual em ${label.toLowerCase()}.`,
          accent: value > 0 ? "Há itens" : "Sem itens"
        }))}
      />

      <Base44Surface className="base44-operation-summary" as="section">
        <div className="base44-operation-summary-head">
          <div>
            <p className="base44-eyebrow">Resumo</p>
            <h2>Operação de estoque</h2>
            <p className="base44-operation-summary-description">
              O shell visual é Apoema, mas a fonte de dados e a leitura operacional seguem a API real.
            </p>
          </div>
          <div className="base44-chip-row">
            <Base44StatusBadge status="auditavel">{total} total</Base44StatusBadge>
            <Base44StatusBadge status="leitura">Sem mock</Base44StatusBadge>
          </div>
        </div>

        {total === 0 ? (
          <Base44EmptyState
            title="Nenhum indicador disponível"
            description="Quando a API retornar totais, eles aparecerão neste painel Apoema."
          />
        ) : (
          <div className="base44-operation-badge-row">
            {labels.map(([label, value]) => (
              <Base44MetricCard key={label} title={label} value={value} description="Indicador operacional real." />
            ))}
          </div>
        )}
      </Base44Surface>
    </div>
  );
}
