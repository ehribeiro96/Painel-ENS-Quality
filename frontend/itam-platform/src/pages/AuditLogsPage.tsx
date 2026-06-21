import { FormEvent, useEffect, useMemo, useState } from "react";
import { HermesStatusPill } from "@/components/brand/HermesStatusPill";
import { SentinelSectionHeader } from "@/components/brand/SentinelSectionHeader";
import { DataTable } from "@/components/DataTable";
import { AlertBlock, EmptyState, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { compactId, formatDateTime } from "@/lib/format";
import type { AuditLog, Page } from "@/lib/types";

type AuditFilters = {
  action: string;
  entity_type: string;
  source: string;
  search: string;
  date_from: string;
  date_to: string;
};

const emptyFilters: AuditFilters = {
  action: "",
  entity_type: "",
  source: "",
  search: "",
  date_from: "",
  date_to: ""
};

const auditActions = ["LOGIN", "LOGOUT", "CREATE", "UPDATE", "DELETE", "MOVE", "IMPORT", "SIGNATURE_GENERATE", "STATUS_CHANGE"];
const auditEntities = ["Asset", "AssetMovement", "ImportJob", "MacroGeneration", "MacroTemplate", "User"];

function formatAuditLabel(value: string | null | undefined, fallback = "-") {
  if (!value) return fallback;
  return value
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .toLowerCase()
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function auditActionTone(action: string | null | undefined) {
  const normalized = (action ?? "").toUpperCase();
  if (normalized.includes("DELETE")) return "danger";
  if (normalized.includes("STATUS_CHANGE")) return "warning";
  if (normalized.includes("UPDATE") || normalized.includes("MOVE") || normalized.includes("IMPORT")) return "warning";
  if (normalized.includes("CREATE") || normalized.includes("LOGIN") || normalized.includes("SIGNATURE_GENERATE")) return "success";
  return "neutral";
}

function auditSourceTone(source: string | null | undefined) {
  const normalized = (source ?? "").toLowerCase();
  if (normalized.includes("auth") || normalized.includes("security")) return "warning";
  if (normalized.includes("legacy")) return "neutral";
  return "info";
}

function describeAuditEvent(item: AuditLog) {
  const base = `${formatAuditLabel(item.action, "Ação não informada")} em ${formatAuditLabel(item.entity, "Entidade não informada")}`;
  return item.entity_id ? `${base} #${compactId(item.entity_id)}` : base;
}

function buildAuditQuery(filters: AuditFilters) {
  const params = new URLSearchParams({ page_size: "25" });
  Object.entries(filters).forEach(([key, value]) => {
    const trimmed = value.trim();
    if (trimmed) params.set(key, trimmed);
  });
  return `?${params.toString()}`;
}

function hasActiveFilters(filters: AuditFilters) {
  return Object.values(filters).some((value) => value.trim().length > 0);
}

function sanitizeAuditDetails(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(sanitizeAuditDetails);
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, item]) => {
        if (/password|token|secret|cookie|authorization|api[_-]?key|private[_-]?key/i.test(key)) {
          return [key, "[redigido]"];
        }
        return [key, sanitizeAuditDetails(item)];
      })
    );
  }
  if (typeof value === "string" && /bearer\s+|sk-|ghp_|akia/i.test(value)) {
    return "[redigido]";
  }
  return value;
}

function AuditDetails({ item }: { item: AuditLog }) {
  if (!item.before && !item.after) {
    return <span className="muted">Sem detalhe técnico.</span>;
  }
  const details = JSON.stringify(
    {
      before: sanitizeAuditDetails(item.before),
      after: sanitizeAuditDetails(item.after)
    },
    null,
    2
  );
  return (
    <details>
      <summary>Ver detalhes</summary>
      <pre className="audit-id">{details}</pre>
    </details>
  );
}

export function AuditLogsPage() {
  const { token } = useAuth();
  const [page, setPage] = useState<Page<AuditLog> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [draftFilters, setDraftFilters] = useState<AuditFilters>(emptyFilters);
  const [appliedFilters, setAppliedFilters] = useState<AuditFilters>(emptyFilters);

  const query = useMemo(() => buildAuditQuery(appliedFilters), [appliedFilters]);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    api
      .audit(token, query)
      .then((data) => {
        setPage(data);
        setError(null);
      })
      .catch(() => setError("Não foi possível carregar auditoria."))
      .finally(() => setLoading(false));
  }, [token, query]);

  function updateFilter(key: keyof AuditFilters, value: string) {
    setDraftFilters((current) => ({ ...current, [key]: value }));
  }

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAppliedFilters(draftFilters);
  }

  function clearFilters() {
    setDraftFilters(emptyFilters);
    setAppliedFilters(emptyFilters);
  }

  const items = page?.items ?? [];
  const activeFilters = hasActiveFilters(appliedFilters);
  const summary = useMemo(() => {
    const distinctActions = new Set(items.map((item) => item.action).filter(Boolean)).size;
    const distinctEntities = new Set(items.map((item) => item.entity).filter(Boolean)).size;
    const lastEvent = items[0]?.created_at ? formatDateTime(items[0].created_at) : "-";
    return { distinctActions, distinctEntities, lastEvent };
  }, [items]);

  return (
    <>
      <SentinelSectionHeader
        chips={<HermesStatusPill state="Auditável">Consulta</HermesStatusPill>}
        eyebrow="Auditoria"
        subtitle="Consulta para rastrear ações do sistema, apoiar investigação operacional e conferir eventos sensíveis."
        title="Auditoria"
      />

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

      <form className="filter-bar audit-toolbar" aria-label="Filtros de auditoria" onSubmit={applyFilters}>
        <label>
          Ação
          <select className="select" value={draftFilters.action} onChange={(event) => updateFilter("action", event.target.value)}>
            <option value="">Todas</option>
            {auditActions.map((action) => <option key={action} value={action}>{formatAuditLabel(action)}</option>)}
          </select>
        </label>
        <label>
          Entidade
          <select className="select" value={draftFilters.entity_type} onChange={(event) => updateFilter("entity_type", event.target.value)}>
            <option value="">Todas</option>
            {auditEntities.map((entity) => <option key={entity} value={entity}>{formatAuditLabel(entity)}</option>)}
          </select>
        </label>
        <label>
          Fonte
          <input className="input" placeholder="api, import..." value={draftFilters.source} onChange={(event) => updateFilter("source", event.target.value)} />
        </label>
        <label>
          Texto / ID / correlação
          <input className="input" placeholder="ID, request, correlation..." value={draftFilters.search} onChange={(event) => updateFilter("search", event.target.value)} />
        </label>
        <label>
          Data inicial
          <input className="input" type="datetime-local" value={draftFilters.date_from} onChange={(event) => updateFilter("date_from", event.target.value)} />
        </label>
        <label>
          Data final
          <input className="input" type="datetime-local" value={draftFilters.date_to} onChange={(event) => updateFilter("date_to", event.target.value)} />
        </label>
        <div className="action-bar">
          <button className="button" type="submit">Aplicar filtros</button>
          <button className="button secondary" type="button" onClick={clearFilters} disabled={!activeFilters && !hasActiveFilters(draftFilters)}>Limpar filtros</button>
        </div>
        <span className={`filter-chip ${activeFilters ? "active" : "muted"}`}>{activeFilters ? "Filtros aplicados" : "Sem filtros aplicados"}</span>
      </form>

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
          emptyMessage="Nenhum registro de auditoria encontrado para os filtros atuais. Limpe os filtros ou ajuste o período/entidade."
          columns={[
            { key: "created_at", label: "Data/Hora", render: (item) => formatDateTime(item.created_at) },
            {
              key: "action",
              label: "Ação",
              render: (item) => (
                <span className={`badge audit-action-badge ${auditActionTone(item.action)}`} title={item.action || "Ação não informada"}>
                  {formatAuditLabel(item.action, "Ação não informada")}
                </span>
              )
            },
            {
              key: "entity",
              label: "Entidade",
              render: (item) => <span title={item.entity || "Entidade não informada"}>{formatAuditLabel(item.entity, "Entidade não informada")}</span>
            },
            {
              key: "description",
              label: "Descrição",
              render: (item) => (
                <span className="audit-event-meta">
                  <strong>{describeAuditEvent(item)}</strong>
                  {item.entity_id ? <small title={item.entity_id}>ID bruto: {compactId(item.entity_id)}</small> : <small>Entidade sem ID.</small>}
                </span>
              )
            },
            {
              key: "actor_id",
              label: "Usuário",
              render: (item) => <span className="audit-id" title={item.actor_id ?? "Usuário não informado"}>{item.actor_id ? compactId(item.actor_id) : "Usuário não informado"}</span>
            },
            {
              key: "source",
              label: "Fonte",
              render: (item) => <span className={`badge audit-source-badge ${auditSourceTone(item.source)}`} title={item.source || "Fonte não informada"}>{formatAuditLabel(item.source, "Fonte não informada")}</span>
            },
            {
              key: "request_id",
              label: "Rastreamento",
              render: (item) => (
                <span className="audit-event-meta">
                  <small title={item.request_id ?? "Correlação não informada"}>Req: {item.request_id ? compactId(item.request_id) : "Correlação não informada"}</small>
                  <small title={item.correlation_id ?? "Correlação não informada"}>Corr: {item.correlation_id ? compactId(item.correlation_id) : "Correlação não informada"}</small>
                </span>
              )
            },
            {
              key: "details",
              label: "Detalhes",
              render: (item) => <AuditDetails item={item} />
            }
          ]}
        />
      </section>
    </>
  );
}
