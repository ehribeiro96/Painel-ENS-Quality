import { FormEvent, useEffect, useMemo, useState } from "react";
import { ArrowLeft, ArrowRight, Search, ShieldAlert } from "lucide-react";

import { Base44AuditEventCard } from "@/components/base44/Base44AuditEventCard";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Button } from "@/components/ui/button";
import { DonorChip, DonorField, DonorFieldGrid, DonorSelect, DonorTextInput } from "../components/DonorForm";
import { DonorPanelPageLayout } from "../components/DonorPanelPageLayout";
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
      .catch(() => setError("Não foi possível carregar os logs de auditoria."))
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
    <DonorPanelPageLayout
      eyebrow="Auditoria operacional"
      title="Logs de Auditoria"
      description="Consulta rastreável com filtros donor-style, paginação e eventos expostos pela API real dentro da experiência Apoema."
      actions={
        <>
          <DonorChip>{page?.total ?? 0} eventos</DonorChip>
          <DonorChip>Página {currentPage}/{totalPages}</DonorChip>
        </>
      }
      stats={[
        { label: "Eventos", value: page?.total ?? 0, detail: "Total retornado pela última consulta." },
        { label: "Ações distintas", value: summary.distinctActions, detail: "Tipos de operação presentes na página atual." },
        { label: "Entidades distintas", value: summary.distinctEntities, detail: "Domínios ou tabelas alcançados." },
        { label: "Rastreáveis", value: summary.traceableEvents, detail: "Linhas com request_id, correlation_id ou entity_id." },
      ]}
    >
      {error ? (
        <Alert tone="danger">
          <strong>{error}</strong>
          <p>Atualize a página, verifique sua sessão e confirme a permissão de auditoria antes de tentar novamente.</p>
        </Alert>
      ) : null}
      {loading ? <LoadingBlock label="Carregando logs de auditoria..." /> : null}

      <section className="rounded-[26px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_50px_-26px_rgba(0,0,0,0.8)]">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Filtros</p>
            <h2 className="mt-2 text-lg font-semibold text-slate-50">Refinar investigação</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">Busca, ação, entidade e campos de rastreabilidade permanecem ligados ao estado real e à query enviada à API.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <DonorChip>{activeFilters ? "Filtros ativos" : "Consulta limpa"}</DonorChip>
            <DonorChip>{loading ? "Atualizando" : "API real"}</DonorChip>
          </div>
        </div>

        <form className="mt-5 space-y-4" aria-label="Filtros de auditoria" onSubmit={applyFilters}>
          <DonorFieldGrid className="grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
            <DonorSelect
              label="Ação"
              value={draftFilters.action}
              placeholder="Todas"
              options={[{ value: "", label: "Todas" }, ...auditActions.map((action) => ({ value: action, label: formatAuditLabel(action) }))]}
              onChange={(value) => updateFilter("action", value)}
            />
            <DonorSelect
              label="Entidade"
              value={draftFilters.entity_type}
              placeholder="Todas"
              options={[{ value: "", label: "Todas" }, ...auditEntities.map((entity) => ({ value: entity, label: formatAuditLabel(entity) }))]}
              onChange={(value) => updateFilter("entity_type", value)}
            />
            <DonorField label="Entity ID">
              <DonorTextInput placeholder="ID do registro" value={draftFilters.entity_id} onChange={(event) => updateFilter("entity_id", event.target.value)} />
            </DonorField>
            <DonorField label="User ID">
              <DonorTextInput placeholder="ID do usuário" value={draftFilters.user_id} onChange={(event) => updateFilter("user_id", event.target.value)} />
            </DonorField>
            <DonorField label="Fonte">
              <DonorTextInput placeholder="api, import..." value={draftFilters.source} onChange={(event) => updateFilter("source", event.target.value)} />
            </DonorField>
            <DonorField label="Request ID">
              <DonorTextInput placeholder="Request ID" value={draftFilters.request_id} onChange={(event) => updateFilter("request_id", event.target.value)} />
            </DonorField>
            <DonorField label="Correlation ID">
              <DonorTextInput placeholder="Correlation ID" value={draftFilters.correlation_id} onChange={(event) => updateFilter("correlation_id", event.target.value)} />
            </DonorField>
            <DonorField label="Texto / busca">
              <DonorTextInput placeholder="ID, request, correlation..." value={draftFilters.search} onChange={(event) => updateFilter("search", event.target.value)} />
            </DonorField>
            <DonorField label="Data inicial">
              <DonorTextInput type="datetime-local" value={draftFilters.date_from} onChange={(event) => updateFilter("date_from", event.target.value)} />
            </DonorField>
            <DonorField label="Data final">
              <DonorTextInput type="datetime-local" value={draftFilters.date_to} onChange={(event) => updateFilter("date_to", event.target.value)} />
            </DonorField>
          </DonorFieldGrid>

          <div className="flex flex-wrap gap-2">
            <Button type="submit" className="rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300">
              <Search className="h-4 w-4" />
              Aplicar filtros
            </Button>
            <Button
              type="button"
              variant="outline"
              className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10"
              onClick={clearFilters}
              disabled={!activeFilters && !hasActiveFilters(draftFilters)}
            >
              Limpar filtros
            </Button>
          </div>
        </form>
      </section>

      <section className="rounded-[26px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_50px_-26px_rgba(0,0,0,0.8)]">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Registros</p>
            <h2 className="mt-2 text-lg font-semibold text-slate-50">Eventos de auditoria</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">Lista operacional com rastreabilidade explícita para investigação e conferência rápida.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <DonorChip>{page?.page_size ?? 25} por página</DonorChip>
            <DonorChip>{page?.total ?? 0} total</DonorChip>
          </div>
        </div>

        {items.length ? (
          <div className="mt-5 grid gap-4 xl:grid-cols-2">
            {items.map((item) => (
              <Base44AuditEventCard item={item} key={item.id} />
            ))}
          </div>
        ) : (
          <Base44EmptyState
            icon={ShieldAlert}
            title="Nenhum evento encontrado"
            description={activeFilters ? "Os filtros atuais não retornaram resultados. Ajuste a busca, a entidade ou a janela de tempo." : "Quando a API retornar eventos, eles aparecerão aqui com cards de auditoria sobre os dados reais."}
            action={<Button type="button" variant="outline" className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10" onClick={clearFilters}>Limpar filtros</Button>}
          />
        )}
      </section>

      <section className="flex flex-wrap items-center justify-between gap-3 rounded-[26px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_50px_-26px_rgba(0,0,0,0.8)]" aria-label="Paginação de auditoria">
        <div className="space-y-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Paginação</p>
          <h2 className="text-lg font-semibold text-slate-50">Página {currentPage} de {totalPages}</h2>
          <p className="text-sm leading-6 text-slate-300">Use os controles abaixo para navegar entre lotes sem alterar o contrato de dados atual.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            type="button"
            variant="outline"
            className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10"
            disabled={navigationDisabled || currentPage <= 1}
            onClick={() => setPageNumber((value) => Math.max(1, value - 1))}
          >
            <ArrowLeft size={16} aria-hidden />
            Anterior
          </Button>
          <Button
            type="button"
            variant="outline"
            className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10"
            disabled={navigationDisabled || currentPage >= totalPages}
            onClick={() => setPageNumber((value) => Math.min(totalPages, value + 1))}
          >
            Próxima
            <ArrowRight size={16} aria-hidden />
          </Button>
        </div>
      </section>
    </DonorPanelPageLayout>
  );
}
