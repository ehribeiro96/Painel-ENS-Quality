import { useEffect, useMemo, useState } from "react";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
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

  return (
    <>
      <div className="page-title">
        <div>
          <h1>Estoque</h1>
          <p>Disponibilidade, reservas, manutencao e retirada operacional.</p>
        </div>
      </div>
      {error ? <Alert tone="danger">{error}</Alert> : null}
      {loading ? <LoadingBlock /> : null}
      <section className="grid metrics">
        {labels.map(([label, value]) => (
          <article className="card" key={label}>
            <div className="metric-label">{label}</div>
            <div className="metric-value">{value}</div>
          </article>
        ))}
      </section>
    </>
  );
}
