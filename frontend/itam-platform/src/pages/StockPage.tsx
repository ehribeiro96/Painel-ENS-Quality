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

const stockLabels = ["STOCK", "RESERVED", "CONFIG_PENDING", "MAINTENANCE", "DEFECTIVE", "DISCARDED"];

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
      .catch(() => setError("Nao foi possivel carregar indicadores de estoque."))
      .finally(() => setLoading(false));
  }, [token]);

  const labels = useMemo(() => stockLabels.map((label) => [label, counts[label] ?? 0] as const), [counts]);
  const total = labels.reduce((sum, [, value]) => sum + value, 0);

  return (
    <div className="base44-operation-page">
      <Base44PageHeader
        eyebrow="Operação de estoque"
        title="Estoque"
        description="Visão visual Base44 para disponibilidade, reservas, manutenção e retirada operacional, preservando a leitura da API real de ativos por status."
        actions={<Base44StatusBadge status={loading ? "warning" : "auditavel"}>{loading ? "Atualizando" : "API real"}</Base44StatusBadge>}
      />

      {error ? <Alert tone="danger">{error}</Alert> : null}
      {loading ? <LoadingBlock /> : null}

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
            <p className="base44-operation-summary-description">A listagem visual foi simplificada, mas os contratos e a fonte de dados continuam os mesmos.</p>
          </div>
          <div className="base44-chip-row">
            <Base44StatusBadge status="auditavel">{total} total</Base44StatusBadge>
            <Base44StatusBadge status="leitura">Sem mock</Base44StatusBadge>
          </div>
        </div>
        {total === 0 ? (
          <Base44EmptyState title="Nenhum indicador disponível" description="Quando a API retornar totais, eles aparecerão neste painel Base44." />
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
