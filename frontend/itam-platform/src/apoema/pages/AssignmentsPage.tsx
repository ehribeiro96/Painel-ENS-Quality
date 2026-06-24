import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { CircleAlert, History, MapPin, Users } from "lucide-react";

import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { DataTable } from "@/components/DataTable";
import { Base44AssetTimeline } from "@/components/base44/Base44AssetTimeline";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44OperationalGrid } from "@/components/base44/Base44OperationalGrid";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
import { api } from "@/lib/api";
import { formatAssetStatus, formatDateTime } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import type { Asset, Movement, Page } from "@/lib/types";

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
    queryKey: ["apoema-assignments", trimmedSearch, status],
    enabled: Boolean(token),
    queryFn: () => {
      const params = new URLSearchParams({ page_size: "200", sort_by: "updated_at", sort_order: "desc" });
      if (trimmedSearch) params.set("search", trimmedSearch);
      if (status === "current") params.set("status", "IN_USE");
      return api.assets(token as string, `?${params.toString()}`);
    }
  });

  const movementsQuery = useQuery({
    queryKey: ["apoema-assignments-recent-movements"],
    enabled: Boolean(token),
    queryFn: () => api.recentMovements(token as string)
  });

  const loadedAssets = (assetsQuery.data as Page<Asset> | undefined)?.items ?? [];
  const recentMovements = (movementsQuery.data ?? []) as Movement[];
  const items = useMemo(() => loadedAssets.filter((asset) => status !== "current" || asset.current_user), [loadedAssets, status]);
  const hasActiveFilter = Boolean(trimmedSearch) || status === "current";
  const linkedAssets = loadedAssets.filter((asset) => asset.current_user).length;
  const unassignedAssets = loadedAssets.filter((asset) => !asset.current_user).length;
  const inUseAssets = loadedAssets.filter((asset) => asset.status === "IN_USE").length;
  const distinctUnits = new Set(loadedAssets.map((asset) => unitFromLocation(asset.location)).filter(Boolean)).size;
  const inconsistentInUse = loadedAssets.filter((asset) => asset.status === "IN_USE" && !asset.current_user).length;
  const recentResponsibleCount = new Set(recentMovements.map((movement) => movement.responsible_id ?? movement.responsible_name ?? movement.asset_id).filter(Boolean)).size;
  const emptyMessage = hasActiveFilter
    ? "Nenhuma movimentação encontrada com os filtros atuais. Ajuste a busca ou altere a visão."
    : "Nenhum ativo ou vínculo retornado pela API real.";

  const summaryItems = [
    {
      title: "Vínculos vigentes",
      value: linkedAssets,
      description: "Ativos com colaborador atual na amostra carregada.",
      icon: Users,
      accent: status === "current" ? "Somente IN_USE" : "Todos os ativos"
    },
    {
      title: "Sem colaborador",
      value: unassignedAssets,
      description: "Ativos carregados sem usuário atual.",
      icon: CircleAlert,
      accent: unassignedAssets > 0 ? "Atenção" : "OK"
    },
    {
      title: "Movimentações recentes",
      value: recentMovements.length,
      description: "Eventos reais retornados pela API de histórico.",
      icon: History,
      accent: recentMovements.length > 0 ? `${recentResponsibleCount} responsável(is)` : "Sem eventos"
    },
    {
      title: "Unidades",
      value: distinctUnits,
      description: "Localizações/unidades distintas na amostra.",
      icon: MapPin,
      accent: inUseAssets > 0 ? `${inUseAssets} em uso` : "Sem uso"
    }
  ];

  return (
    <div className="base44-operation-page">
      <Base44PageHeader
        eyebrow="Apoema Movimentações"
        title="Movimentações"
        description="Visão operacional dos vínculos atuais entre ativos e colaboradores, com histórico recente de movimentações e dados reais da API."
        actions={
          <>
            <Base44StatusBadge status={assetsQuery.isLoading || movementsQuery.isLoading ? "warning" : "auditavel"}>
              {assetsQuery.isLoading || movementsQuery.isLoading ? "Atualizando" : "API real"}
            </Base44StatusBadge>
            <Link className="button secondary" to="/assets">
              Abrir ativos
            </Link>
          </>
        }
      />

      <Base44OperationalGrid
        title="Resumo da movimentação"
        description="Os cartões abaixo refletem os vínculos atuais e a trilha recente retornada pela API."
        columns={4}
        items={summaryItems}
      />

      {assetsQuery.isError ? (
        <Alert tone="danger">
          <strong>Não foi possível carregar as movimentações.</strong>
          <p>Atualize a página, confirme sua sessão e valide a disponibilidade da API antes de tentar novamente.</p>
        </Alert>
      ) : null}
      {movementsQuery.isError ? (
        <Alert tone="warning">
          <strong>O histórico recente não pôde ser carregado.</strong>
          <p>A visão de vínculos permanece disponível, mas a trilha cronológica ficará vazia até a API responder.</p>
        </Alert>
      ) : null}
      {assetsQuery.isLoading || movementsQuery.isLoading ? <LoadingBlock label="Carregando movimentações..." /> : null}
      {inconsistentInUse > 0 ? (
        <Alert tone="warning">
          <strong>{inconsistentInUse} ativo(s) em uso sem colaborador atual nos dados carregados.</strong>
          <p>Revise o cadastro do ativo ou consulte o histórico antes de tomar ação operacional. Nenhum dado foi alterado por esta tela.</p>
        </Alert>
      ) : null}

      <section className="base44-operation-columns">
        <Base44Surface className="base44-operation-panel" as="section">
          <div className="base44-operation-panel-head">
            <div>
              <p className="base44-eyebrow">Vínculos atuais</p>
              <h2>Ativos vinculados</h2>
              <p className="base44-operation-panel-description">Tabela baseada nos ativos retornados pela API atual. “Atualizado em” é referência do ativo, não início histórico do vínculo.</p>
            </div>
            <Base44StatusBadge status={hasActiveFilter ? "auditavel" : "leitura"}>{items.length} registro(s)</Base44StatusBadge>
          </div>

          <section className="filter-bar assignments-toolbar" aria-label="Filtros de movimentações">
            <label className="wide-field">
              Busca
              <input
                className="input full"
                placeholder="Buscar por tag, colaborador, identificador ou e-mail..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
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

          <DataTable
            items={items}
            emptyMessage={emptyMessage}
            columns={[
              {
                key: "hostname",
                label: "Ativo",
                render: (asset) => (
                  <span className="assignment-cell">
                    <Link to={`/assets/${asset.id}`} title={assetDisplayName(asset)}>
                      {assetDisplayName(asset)}
                    </Link>
                    <small title={assetSubtitle(asset)}>{assetSubtitle(asset)}</small>
                  </span>
                )
              },
              { key: "asset_type", label: "Tipo", render: (asset) => <span className="badge neutral">{asset.asset_type}</span> },
              {
                key: "current_user",
                label: "Colaborador atual",
                render: (asset) => (asset.current_user ? (
                  <span className="assignment-cell">
                    <strong title={asset.current_user.name}>{asset.current_user.name}</strong>
                    <small title={asset.current_user.email}>{asset.current_user.email}</small>
                  </span>
                ) : (
                  <span className="assignment-warning">Sem colaborador</span>
                ))
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
        </Base44Surface>

        <Base44Surface className="base44-operation-panel" as="section">
          <div className="base44-operation-panel-head">
            <div>
              <p className="base44-eyebrow">Histórico recente</p>
              <h2>Movimentações auditáveis</h2>
              <p className="base44-operation-panel-description">A trilha mostra antes e depois de cada movimentação real retornada pela API.</p>
            </div>
            <Base44StatusBadge status={recentMovements.length ? "success" : "warning"}>
              {recentMovements.length ? `${recentMovements.length} evento(s)` : "Sem eventos"}
            </Base44StatusBadge>
          </div>

          {recentMovements.length > 0 ? (
            <Base44AssetTimeline movements={recentMovements} />
          ) : (
            <Base44EmptyState
              title="Nenhuma movimentação recente"
              description="Quando a API retornar histórico, a linha do tempo mostrará as mudanças de usuário, status e localização."
            />
          )}
        </Base44Surface>
      </section>
    </div>
  );
}
