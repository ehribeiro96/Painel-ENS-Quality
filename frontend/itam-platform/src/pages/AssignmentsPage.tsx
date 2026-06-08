import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { DataTable } from "@/components/DataTable";
import { AlertBlock, EmptyState, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatAssetStatus, formatDateTime } from "@/lib/format";
import type { Asset, Page } from "@/lib/types";

function assetDisplayName(asset: Asset) {
  return asset.patrimony ?? asset.hostname ?? asset.serial ?? asset.id.slice(0, 8);
}

function assetSubtitle(asset: Asset) {
  const parts = [asset.hostname, asset.serial].filter(Boolean);
  return parts.length ? parts.join(" • ") : "Sem hostname/serial informado";
}

function statusTone(status: string) {
  if (status === "IN_USE" || status === "STOCK") return "success";
  if (status === "MAINTENANCE" || status === "RESERVED" || status === "CONFIG_PENDING") return "warning";
  if (status === "DEFECTIVE" || status === "DISCARDED") return "danger";
  return "neutral";
}

function unitFromLocation(location: string | null | undefined) {
  return location?.split("-")[0]?.trim() || null;
}

export function AssignmentsPage() {
  const { token } = useAuth();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("current");
  const trimmedSearch = search.trim();
  const assetsQuery = useQuery({
    queryKey: ["assignments", search, status],
    enabled: Boolean(token),
    queryFn: () => {
      const params = new URLSearchParams({ page_size: "200", sort_by: "updated_at", sort_order: "desc" });
      if (trimmedSearch) params.set("search", trimmedSearch);
      if (status === "current") params.set("status", "IN_USE");
      return api.assets(token as string, `?${params.toString()}`);
    }
  });

  const loadedAssets = (assetsQuery.data as Page<Asset> | undefined)?.items ?? [];
  const items = useMemo(
    () => loadedAssets.filter((asset) => status !== "current" || asset.current_user),
    [loadedAssets, status]
  );
  const hasActiveFilter = Boolean(trimmedSearch) || status === "current";
  const linkedAssets = loadedAssets.filter((asset) => asset.current_user).length;
  const unassignedAssets = loadedAssets.filter((asset) => !asset.current_user).length;
  const inUseAssets = loadedAssets.filter((asset) => asset.status === "IN_USE").length;
  const distinctUnits = new Set(loadedAssets.map((asset) => unitFromLocation(asset.location)).filter(Boolean)).size;
  const inconsistentInUse = loadedAssets.filter((asset) => asset.status === "IN_USE" && !asset.current_user).length;
  const emptyMessage = hasActiveFilter
    ? "Nenhuma atribuição encontrada com os filtros atuais. Ajuste a busca ou altere a visão."
    : "Nenhum ativo ou vínculo retornado pela API atual.";

  return (
    <>
      <header className="page-title page-header assignments-page-header">
        <div>
          <span className="badge info">Visão atual</span>
          <h1>Atribuições</h1>
          <p>Visão operacional dos vínculos atuais entre ativos e colaboradores. Esta tela não substitui histórico completo de movimentações.</p>
        </div>
        <div className="page-actions">
          <span className="badge neutral">Consulta</span>
        </div>
      </header>

      <section className="assignments-summary-grid" aria-label="Resumo de atribuições">
        {loadedAssets.length ? (
          <>
            <article className="card assignment-summary-card">
              <span>Exibidos</span>
              <strong>{items.length}</strong>
              <p>Linhas visíveis após a visão selecionada.</p>
            </article>
            <article className="card assignment-summary-card">
              <span>Vinculados</span>
              <strong>{linkedAssets}</strong>
              <p>Ativos com colaborador atual nos dados carregados.</p>
            </article>
            <article className="card assignment-summary-card">
              <span>Sem colaborador</span>
              <strong>{unassignedAssets}</strong>
              <p>Ativos carregados sem usuário atual.</p>
            </article>
            <article className="card assignment-summary-card">
              <span>Em uso</span>
              <strong>{inUseAssets}</strong>
              <p>Ativos carregados com status Em uso.</p>
            </article>
            <article className="card assignment-summary-card">
              <span>Unidades</span>
              <strong>{distinctUnits}</strong>
              <p>Localizações/unidades distintas na amostra.</p>
            </article>
          </>
        ) : (
          <div className="card assignments-summary-empty">
            <EmptyState title="Sem dados para resumir." description="Quando a API retornar ativos, esta área mostrará os vínculos e sinais operacionais da visão carregada." />
          </div>
        )}
      </section>

      <section className="filter-bar assignments-toolbar" aria-label="Filtros de atribuições">
        <label className="wide-field">
          Busca
          <input className="input full" placeholder="Buscar por tag, colaborador, identificador ou e-mail..." value={search} onChange={(event) => setSearch(event.target.value)} />
        </label>
        <label>
          Visão
          <select className="select full" value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="current">Vínculos atuais</option>
            <option value="all">Todos os ativos</option>
          </select>
        </label>
        <span className={`filter-chip ${trimmedSearch ? "active" : ""}`}>{trimmedSearch ? `Busca ativa: ${trimmedSearch}` : "Sem busca ativa"}</span>
        <span className={`filter-chip ${status === "current" ? "active" : "neutral"}`}>{status === "current" ? "Mostrando IN_USE com colaborador" : "Mostrando todos os ativos carregados"}</span>
      </section>

      {inconsistentInUse > 0 ? (
        <AlertBlock tone="warning">
          <strong>{inconsistentInUse} ativo(s) em uso sem colaborador atual nos dados carregados.</strong>
          <p>Revise o cadastro do ativo ou consulte o histórico antes de tomar ação operacional. Nenhum dado foi alterado por esta tela.</p>
        </AlertBlock>
      ) : null}

      {assetsQuery.isError ? (
        <AlertBlock tone="danger">
          <strong>Não foi possível carregar as atribuições.</strong>
          <p>Atualize a página, verifique se sua sessão ainda está ativa, confirme sua permissão e consulte os logs do backend se o problema continuar.</p>
        </AlertBlock>
      ) : null}
      {assetsQuery.isLoading ? <LoadingBlock label="Carregando atribuições..." /> : null}

      <section className="card assignments-table-card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Vínculos de ativos</h2>
            <p className="card-description">Tabela baseada nos ativos retornados pela API atual. “Atualizado em” é referência do ativo, não início histórico do vínculo.</p>
          </div>
          <span className={`badge ${hasActiveFilter ? "info" : "neutral"}`}>{items.length} atribuição(ões)</span>
        </div>
        <DataTable
          items={items}
          emptyMessage={emptyMessage}
          columns={[
            {
              key: "hostname",
              label: "Ativo",
              render: (asset) => (
                <span className="assignment-cell">
                  <Link to={`/assets/${asset.id}`} title={assetDisplayName(asset)}>{assetDisplayName(asset)}</Link>
                  <small title={assetSubtitle(asset)}>{assetSubtitle(asset)}</small>
                </span>
              )
            },
            { key: "asset_type", label: "Tipo", render: (asset) => <span className="badge neutral">{asset.asset_type}</span> },
            {
              key: "current_user",
              label: "Colaborador atual",
              render: (asset) => asset.current_user ? (
                <span className="assignment-cell">
                  <strong title={asset.current_user.name}>{asset.current_user.name}</strong>
                  <small title={asset.current_user.email}>{asset.current_user.email}</small>
                </span>
              ) : <span className="assignment-warning">Sem colaborador</span>
            },
            { key: "user_login", label: "Identificador", render: (asset) => asset.current_user?.email?.split("@")[0] ?? "-" },
            {
              key: "location",
              label: "Localização",
              render: (asset) => (
                <span className="assignment-meta" title={asset.location ?? "Sem localização"}>
                  <strong>{unitFromLocation(asset.location) ?? "-"}</strong>
                  <small>{asset.location ?? "Sem localização"}</small>
                </span>
              )
            },
            { key: "updated_at", label: "Atualizado em", render: (asset) => formatDateTime(asset.updated_at) },
            {
              key: "status",
              label: "Status",
              render: (asset) => <span className={`badge assignment-status-badge ${statusTone(asset.status)}`}>{formatAssetStatus(asset.status)}</span>
            }
          ]}
        />
      </section>
    </>
  );
}
