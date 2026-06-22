import { FormEvent, useEffect, useMemo, useState } from "react";
import { ArrowLeft, ArrowRight, Search, ShieldAlert } from "lucide-react";

import { Base44AuditEventCard } from "@/components/base44/Base44AuditEventCard";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44FilterPanel } from "@/components/base44/Base44FilterPanel";
import { Base44InfoGrid } from "@/components/base44/Base44InfoGrid";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
import { AlertBlock, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { AuditLog, Page } from "@/lib/types";

type AuditFilters = {
  action: string;
  entity_type: string;
  entity_id: string;
  user_id: string;
  source: string;
  correlation_id: string;
  request_id: string;
  search: string;
  date_from: string;
  date_to: string;
};

const emptyFilters: AuditFilters = {
  action: "",
  entity_type: "",
  entity_id: "",
  user_id: "",
  source: "",
  correlation_id: "",
  request_id: "",
  search: "",
  date_from: "",
  date_to: "",
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

function buildAuditQuery(filters: AuditFilters, pageNumber: number) {
  const params = new URLSearchParams({ page_size: "25", page: String(pageNumber) });
  Object.entries(filters).forEach(([key, value]) => {
    const trimmed = value.trim();
    if (trimmed) params.set(key, trimmed);
  });
  return `?${params.toString()}`;
}

function hasActiveFilters(filters: AuditFilters) {
  return Object.values(filters).some((value) => value.trim().length > 0);
}

function hasTraceableFields(item: AuditLog) {
  return Boolean(item.request_id || item.correlation_id || item.entity_id || item.actor_id);
}

export function AuditLogsPage() {
  const { token } = useAuth();
  const [page, setPage] = useState<Page<AuditLog> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [draftFilters, setDraftFilters] = useState<AuditFilters>(emptyFilters);
  const [appliedFilters, setAppliedFilters] = useState<AuditFilters>(emptyFilters);
  const [pageNumber, setPageNumber] = useState(1);

  const query = useMemo(() => buildAuditQuery(appliedFilters, pageNumber), [appliedFilters, pageNumber]);

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
    setPageNumber(1);
    setAppliedFilters(draftFilters);
  }

  function clearFilters() {
    setDraftFilters(emptyFilters);
    setAppliedFilters(emptyFilters);
    setPageNumber(1);
  }

  const items = page?.items ?? [];
  const activeFilters = hasActiveFilters(appliedFilters);
  const totalPages = page ? Math.max(1, Math.ceil(page.total / page.page_size)) : 1;
  const currentPage = page?.page ?? pageNumber;
  const summary = useMemo(() => {
    const distinctActions = new Set(items.map((item) => item.action).filter(Boolean)).size;
    const distinctEntities = new Set(items.map((item) => item.entity).filter(Boolean)).size;
    const traceableEvents = items.filter(hasTraceableFields).length;
    const lastEvent = items[0]?.created_at ? new Date(items[0].created_at).toLocaleString("pt-BR") : "-";
    return { distinctActions, distinctEntities, traceableEvents, lastEvent };
  }, [items]);

  const navigationDisabled = loading || !items.length;

  return (
    <div className="base44-audit-page">
      <Base44PageHeader
        eyebrow="Auditoria operacional"
        title="Auditoria"
        description="Consulta com rastreabilidade completa, filtros preservados e navegação por página sobre os eventos expostos pela API real."
        breadcrumbs={[
          <span key="root">Operações</span>,
          <span key="sep">/</span>,
          <span key="audit">Auditoria</span>,
        ]}
        actions={
          <>
            <Base44StatusBadge status="auditavel">{page?.total ?? 0} eventos</Base44StatusBadge>
            <Base44StatusBadge status="auditavel">Página {currentPage}/{totalPages}</Base44StatusBadge>
          </>
        }
      />

      <section className="grid base44-audit-summary-grid" aria-label="Resumo de auditoria">
        <Base44InfoGrid
          columns={4}
          title="Visão rápida"
          items={[
            { label: "Eventos carregados", value: page?.total ?? 0, hint: "Total retornado pela última consulta." },
            { label: "Ações distintas", value: summary.distinctActions, hint: "Tipos de operação presentes na página atual." },
            { label: "Entidades distintas", value: summary.distinctEntities, hint: "Domínios ou tabelas alcançados pelos eventos." },
            { label: "Eventos rastreáveis", value: summary.traceableEvents, hint: "Linhas com request_id, correlation_id ou entity_id." },
          ]}
        />
        <Base44Surface className="base44-audit-summary-card" as="aside">
          <p className="base44-eyebrow">Último evento</p>
          <h2>{summary.lastEvent}</h2>
          <p className="base44-audit-summary-copy">
            Os campos de rastreabilidade continuam expostos nos cards, e a consulta segue enviando entity_type, entity_id, user_id, request_id e correlation_id quando preenchidos.
          </p>
          <div className="base44-chip-row">
            <Base44StatusBadge status="auditavel">{activeFilters ? "Filtros ativos" : "Consulta limpa"}</Base44StatusBadge>
            <Base44StatusBadge status="auditavel">{loading ? "Atualizando" : "API real"}</Base44StatusBadge>
          </div>
        </Base44Surface>
      </section>

      <Base44FilterPanel
        eyebrow="Filtros de auditoria"
        title="Refinar investigação"
        description="Busca, ação, entidade e campos de rastreabilidade permanecem ligados ao estado real e à query enviada à API."
        actions={
          <div className="base44-chip-row">
            <Base44StatusBadge status={activeFilters ? "warning" : "leitura"}>{activeFilters ? "Aplicados" : "Sem filtros"}</Base44StatusBadge>
          </div>
        }
      >
        <form className="b44-filter-grid" aria-label="Filtros de auditoria" onSubmit={applyFilters}>
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
            Entity ID
            <input className="input" placeholder="ID do registro" value={draftFilters.entity_id} onChange={(event) => updateFilter("entity_id", event.target.value)} />
          </label>
          <label>
            User ID
            <input className="input" placeholder="ID do usuário" value={draftFilters.user_id} onChange={(event) => updateFilter("user_id", event.target.value)} />
          </label>
          <label>
            Fonte
            <input className="input" placeholder="api, import..." value={draftFilters.source} onChange={(event) => updateFilter("source", event.target.value)} />
          </label>
          <label>
            Request ID
            <input className="input" placeholder="Request ID" value={draftFilters.request_id} onChange={(event) => updateFilter("request_id", event.target.value)} />
          </label>
          <label>
            Correlation ID
            <input className="input" placeholder="Correlation ID" value={draftFilters.correlation_id} onChange={(event) => updateFilter("correlation_id", event.target.value)} />
          </label>
          <label>
            Texto / busca
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
          <div className="b44-filter-actions">
            <button className="button" type="submit"><Search size={16} aria-hidden /> Aplicar filtros</button>
            <button className="button secondary" type="button" onClick={clearFilters} disabled={!activeFilters && !hasActiveFilters(draftFilters)}>Limpar filtros</button>
          </div>
        </form>
      </Base44FilterPanel>

      {error ? (
        <AlertBlock tone="danger">
          <strong>{error}</strong>
          <p>Atualize a página, verifique sua sessão e confirme a permissão de auditoria antes de tentar novamente.</p>
        </AlertBlock>
      ) : null}
      {loading ? <LoadingBlock label="Carregando registros de auditoria..." /> : null}

      <Base44Surface className="base44-audit-collection" as="section">
        <div className="base44-audit-collection-head">
          <div>
            <p className="base44-eyebrow">Registros</p>
            <h2>Eventos de auditoria</h2>
            <p className="base44-audit-collection-description">Lista operacional com rastreabilidade explícita para investigação e conferência rápida.</p>
          </div>
          <div className="base44-chip-row">
            <Base44StatusBadge status="auditavel">{page?.page_size ?? 25} por página</Base44StatusBadge>
            <Base44StatusBadge status="auditavel">{page?.total ?? 0} total</Base44StatusBadge>
          </div>
        </div>

        {items.length ? (
          <div className="base44-audit-events-grid">
            {items.map((item) => <Base44AuditEventCard item={item} key={item.id} />)}
          </div>
        ) : (
          <Base44EmptyState
            icon={ShieldAlert}
            title="Nenhum evento encontrado"
            description={activeFilters ? "Os filtros atuais não retornaram resultados. Ajuste a busca, a entidade ou a janela de tempo." : "Quando a API retornar eventos, eles aparecerão aqui com cards de auditoria Base44 sobre os dados reais."}
            action={<button className="button secondary" type="button" onClick={clearFilters}>Limpar filtros</button>}
          />
        )}
      </Base44Surface>

      <Base44Surface className="base44-pagination-panel" as="nav" aria-label="Paginação de auditoria">
        <div className="base44-pagination-copy">
          <p className="base44-eyebrow">Paginação</p>
          <h2>Página {currentPage} de {totalPages}</h2>
          <p>Use os controles abaixo para navegar entre lotes sem alterar o contrato de dados atual.</p>
        </div>
        <div className="base44-pagination-actions">
          <button className="button secondary" type="button" disabled={navigationDisabled || currentPage <= 1} onClick={() => setPageNumber((value) => Math.max(1, value - 1))}>
            <ArrowLeft size={16} aria-hidden /> Anterior
          </button>
          <button className="button secondary" type="button" disabled={navigationDisabled || currentPage >= totalPages} onClick={() => setPageNumber((value) => Math.min(totalPages, value + 1))}>
            Próxima <ArrowRight size={16} aria-hidden />
          </button>
        </div>
      </Base44Surface>
    </div>
  );
}
