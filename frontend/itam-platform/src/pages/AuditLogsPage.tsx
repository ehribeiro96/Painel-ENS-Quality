import { useEffect, useMemo, useState } from "react";
import { DataTable } from "@/components/DataTable";
import { AlertBlock, EmptyState, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { compactId, formatDateTime } from "@/lib/format";
import type { AuditLog, Page } from "@/lib/types";

function formatAuditLabel(value: string | null | undefined) {
  if (!value) return "-";
  return value
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .toLowerCase()
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function auditActionTone(action: string) {
  const normalized = action.toUpperCase();
  if (normalized.includes("DELETE")) return "danger";
  if (normalized.includes("STATUS_CHANGE")) return "warning";
  if (normalized.includes("UPDATE") || normalized.includes("MOVE") || normalized.includes("IMPORT")) return "warning";
  if (normalized.includes("CREATE") || normalized.includes("LOGIN") || normalized.includes("SIGNATURE_GENERATE")) return "success";
  return "neutral";
}

function auditSourceTone(source: string) {
  const normalized = source.toLowerCase();
  if (normalized.includes("auth") || normalized.includes("security")) return "warning";
  if (normalized.includes("legacy")) return "neutral";
  return "info";
}

function describeAuditEvent(item: AuditLog) {
  const base = `${formatAuditLabel(item.action)} em ${formatAuditLabel(item.entity)}`;
  return item.entity_id ? `${base} #${compactId(item.entity_id)}` : base;
}

export function AuditLogsPage() {
  const { token } = useAuth();
  const [page, setPage] = useState<Page<AuditLog> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    api
      .audit(token)
      .then((data) => {
        setPage(data);
        setError(null);
      })
      .catch(() => setError("Não foi possível carregar auditoria."))
      .finally(() => setLoading(false));
  }, [token]);

  const items = page?.items ?? [];
  const summary = useMemo(() => {
    const distinctActions = new Set(items.map((item) => item.action).filter(Boolean)).size;
    const distinctEntities = new Set(items.map((item) => item.entity).filter(Boolean)).size;
    const lastEvent = items[0]?.created_at ? formatDateTime(items[0].created_at) : "-";
    return { distinctActions, distinctEntities, lastEvent };
  }, [items]);

  return (
    <>
      <header className="page-title page-header audit-page-header">
        <div>
          <span className="badge info">Auditoria</span>
          <h1>Auditoria</h1>
          <p>Consulta para rastrear ações do sistema, apoiar investigação operacional e conferir eventos sensíveis.</p>
        </div>
        <div className="page-actions">
          <span className="badge neutral">Consulta</span>
        </div>
      </header>

      <section className="audit-summary-grid" aria-label="Resumo de auditoria">
        {items.length ? (
          <>
            <article className="card audit-summary-card">
              <span>Total carregado</span>
              <strong>{items.length}</strong>
              <p>Eventos exibidos nesta página.</p>
            </article>
            <article className="card audit-summary-card">
              <span>Ações distintas</span>
              <strong>{summary.distinctActions}</strong>
              <p>Tipos de operação presentes na amostra.</p>
            </article>
            <article className="card audit-summary-card">
              <span>Entidades distintas</span>
              <strong>{summary.distinctEntities}</strong>
              <p>Tabelas ou domínios envolvidos.</p>
            </article>
            <article className="card audit-summary-card">
              <span>Último evento</span>
              <strong>{summary.lastEvent}</strong>
              <p>Registro mais recente retornado pela API.</p>
            </article>
          </>
        ) : (
          <div className="card audit-summary-empty">
            <EmptyState title="Sem eventos para resumir." description="Quando a API retornar registros, esta área mostrará totais operacionais da auditoria carregada." />
          </div>
        )}
      </section>

      <section className="filter-bar audit-toolbar" aria-label="Filtros de auditoria">
        <span className="filter-chip muted">Busca avançada: em breve</span>
        <span className="filter-chip muted">Ação: em breve</span>
        <span className="filter-chip muted">Entidade: em breve</span>
        <span className="filter-chip muted">Período: em breve</span>
        <p>Filtros avançados dependem de suporte da API. Esta tela mostra os registros retornados pelo endpoint atual.</p>
      </section>

      {error ? (
        <AlertBlock tone="danger">
          <strong>{error}</strong>
          <p>Atualize a página, verifique se sua sessão ainda está ativa, confirme sua permissão e consulte os logs do backend se o problema continuar.</p>
        </AlertBlock>
      ) : null}
      {loading ? <LoadingBlock label="Carregando registros de auditoria..." /> : null}

      <section className="card audit-table-card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Registros de auditoria</h2>
            <p className="card-description">Eventos técnicos retornados pela API, com IDs preservados para rastreio quando disponíveis.</p>
          </div>
          <span className="badge neutral">{page?.total ?? 0} registro(s)</span>
        </div>
        <DataTable
          items={items}
          emptyMessage="Nenhum registro de auditoria encontrado. Execute ações no sistema ou verifique se seu perfil tem permissão para consultar auditoria."
          columns={[
            { key: "created_at", label: "Data/Hora", render: (item) => formatDateTime(item.created_at) },
            {
              key: "action",
              label: "Ação",
              render: (item) => (
                <span className={`badge audit-action-badge ${auditActionTone(item.action)}`} title={item.action}>
                  {formatAuditLabel(item.action)}
                </span>
              )
            },
            {
              key: "entity",
              label: "Tabela/Entidade",
              render: (item) => <span title={item.entity}>{formatAuditLabel(item.entity)}</span>
            },
            {
              key: "description",
              label: "Descrição",
              render: (item) => (
                <span className="audit-event-meta">
                  <strong>{describeAuditEvent(item)}</strong>
                  {item.entity_id ? <small title={item.entity_id}>ID bruto: {compactId(item.entity_id)}</small> : null}
                </span>
              )
            },
            {
              key: "actor_id",
              label: "Usuário",
              render: (item) => <span className="audit-id" title={item.actor_id ?? "Sistema"}>{compactId(item.actor_id) || "Sistema"}</span>
            },
            {
              key: "source",
              label: "Fonte",
              render: (item) => <span className={`badge audit-source-badge ${auditSourceTone(item.source)}`} title={item.source}>{formatAuditLabel(item.source)}</span>
            },
            {
              key: "request_id",
              label: "Rastreamento",
              render: (item) => (
                <span className="audit-event-meta">
                  <small title={item.request_id ?? ""}>Req: {compactId(item.request_id)}</small>
                  <small title={item.correlation_id ?? ""}>Corr: {compactId(item.correlation_id)}</small>
                </span>
              )
            }
          ]}
        />
      </section>
    </>
  );
}
