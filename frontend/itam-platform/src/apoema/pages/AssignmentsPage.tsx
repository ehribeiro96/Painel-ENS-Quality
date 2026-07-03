import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { CircleAlert, History, MapPin, Users } from "lucide-react";

import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Button } from "@/components/ui/button";
import { DonorSelect } from "../components/DonorForm";
import { DonorPanelPageLayout } from "../components/DonorPanelPageLayout";
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
    },
  });

  const movementsQuery = useQuery({
    queryKey: ["apoema-assignments-recent-movements"],
    enabled: Boolean(token),
    queryFn: () => api.recentMovements(token as string),
  });

  const loadedAssets = (assetsQuery.data as Page<Asset> | undefined)?.items ?? [];
  const recentMovements = (movementsQuery.data ?? []) as Movement[];
  const items = useMemo(() => loadedAssets.filter((asset) => status !== "current" || asset.current_user), [loadedAssets, status]);
  const linkedAssets = loadedAssets.filter((asset) => asset.current_user).length;
  const unassignedAssets = loadedAssets.filter((asset) => !asset.current_user).length;
  const inUseAssets = loadedAssets.filter((asset) => asset.status === "IN_USE").length;
  const distinctUnits = new Set(loadedAssets.map((asset) => unitFromLocation(asset.location)).filter(Boolean)).size;
  const inconsistentInUse = loadedAssets.filter((asset) => asset.status === "IN_USE" && !asset.current_user).length;
  const recentResponsibleCount = new Set(recentMovements.map((movement) => movement.responsible_id ?? movement.responsible_name ?? movement.asset_id).filter(Boolean)).size;

  const emptyMessage = trimmedSearch
    ? `Nenhum ativo encontrado para “${trimmedSearch}”. Ajuste a busca e tente novamente.`
    : "Nenhum ativo ou vínculo retornado pela API real.";

  const summaryItems = [
    { title: "Vínculos vigentes", value: linkedAssets, description: "Ativos com colaborador atual." },
    { title: "Sem colaborador", value: unassignedAssets, description: "Ativos carregados sem usuário atual." },
    { title: "Movimentações recentes", value: recentMovements.length, description: "Eventos reais retornados pela API." },
    { title: "Unidades", value: distinctUnits, description: "Localizações distintas na amostra." },
  ];

  return (
    <DonorPanelPageLayout
      eyebrow="Movimentações"
      title="Vínculos e histórico auditável"
      description="Visão operacional dos vínculos atuais entre ativos e colaboradores, com histórico recente e dados reais da API."
      actions={
        <>
          <Button asChild variant="outline" className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10">
            <Link to="/apoema/assets">Abrir ativos</Link>
          </Button>
          <Button asChild className="rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300">
            <Link to="/apoema/chat">Perguntar ao Hermes</Link>
          </Button>
        </>
      }
      stats={summaryItems.map((item) => ({ label: item.title, value: item.value, detail: item.description }))}
    >
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
          <strong>{inconsistentInUse} ativo(s) em uso sem colaborador atual.</strong>
          <p>Revise o cadastro do ativo ou consulte o histórico antes de tomar ação operacional.</p>
        </Alert>
      ) : null}

      <section className="grid min-w-0 gap-4 xl:grid-cols-[minmax(0,1.3fr)_minmax(0,0.9fr)]">
        <article className="min-w-0 rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Vínculos atuais</p>
              <h3 className="mt-1 text-lg font-semibold text-slate-50">Ativos vinculados</h3>
              <p className="mt-1 text-sm leading-6 text-slate-400">Tabela baseada nos ativos retornados pela API atual.</p>
            </div>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">{items.length} registro(s)</span>
          </div>

          <div className="flex flex-wrap gap-3 rounded-[22px] border border-white/10 bg-slate-950/40 p-4">
            <label className="flex min-w-[240px] flex-1 items-center gap-2 rounded-2xl border border-white/10 bg-slate-950/50 px-3 py-3 text-slate-300">
              <span className="text-xs uppercase tracking-[0.18em] text-slate-500">Busca</span>
              <input
                className="w-full bg-transparent text-sm outline-none placeholder:text-slate-500"
                placeholder="Buscar por tag, colaborador, identificador ou e-mail..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </label>
            <DonorSelect
              className="min-w-[220px] flex-1"
              label="Visão"
              value={status}
              options={[
                { value: "current", label: "Vínculos atuais" },
                { value: "all", label: "Todos os ativos" },
              ]}
              onChange={setStatus}
            />
          </div>

          <div className="mt-4 overflow-hidden rounded-[24px] border border-white/10">
            <div className="overflow-x-auto">
              <table className="min-w-full border-collapse text-left text-sm">
                <thead className="bg-slate-950/70 text-slate-300">
                  <tr>
                    {["Ativo", "Tipo", "Colaborador atual", "Identificador", "Localização", "Atualizado em", "Status"].map((header) => (
                      <th key={header} className="whitespace-nowrap px-4 py-3 text-xs font-semibold uppercase tracking-[0.18em]">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10 bg-slate-950/35">
                  {items.length === 0 ? (
                    <tr>
                      <td className="px-4 py-8" colSpan={7}>
                        <div className="rounded-[22px] border border-dashed border-white/15 bg-slate-950/35 p-5 text-slate-300">{emptyMessage}</div>
                      </td>
                    </tr>
                  ) : (
                    items.map((asset) => (
                      <tr key={asset.id} className="align-top">
                        <td className="px-4 py-4">
                          <div className="space-y-1">
                            <Link to={`/apoema/assets/${asset.id}`} className="font-medium text-slate-50 hover:underline">
                              {assetDisplayName(asset)}
                            </Link>
                            <p className="text-xs text-slate-400">{assetSubtitle(asset)}</p>
                          </div>
                        </td>
                        <td className="px-4 py-4 text-slate-300">{asset.asset_type}</td>
                        <td className="px-4 py-4">
                          {asset.current_user ? (
                            <div className="space-y-1">
                              <strong className="block text-slate-50">{asset.current_user.name}</strong>
                              <p className="text-xs text-slate-400">{asset.current_user.email}</p>
                            </div>
                          ) : (
                            <span className="rounded-full border border-amber-300/20 bg-amber-400/10 px-3 py-1 text-xs text-amber-100">Sem colaborador</span>
                          )}
                        </td>
                        <td className="px-4 py-4 text-slate-300">{asset.current_user?.email?.split("@")[0] ?? "-"}</td>
                        <td className="px-4 py-4 text-slate-300">
                          <div className="space-y-1">
                            <strong className="block text-slate-100">{unitFromLocation(asset.location) ?? "-"}</strong>
                            <p className="text-xs text-slate-400">{asset.location ?? "Sem localização"}</p>
                          </div>
                        </td>
                        <td className="px-4 py-4 text-slate-300">{formatDateTime(asset.updated_at)}</td>
                        <td className="px-4 py-4">
                          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">{formatAssetStatus(asset.status)}</span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </article>

        <article className="min-w-0 rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Histórico recente</p>
              <h3 className="mt-1 text-lg font-semibold text-slate-50">Movimentações auditáveis</h3>
              <p className="mt-1 text-sm leading-6 text-slate-400">A trilha mostra antes e depois de cada movimentação real.</p>
            </div>
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-100">
              <History className="h-4 w-4" />
            </span>
          </div>

          <div className="space-y-3">
            {recentMovements.length > 0 ? (
              recentMovements.map((movement) => (
                <article key={movement.id} className="rounded-[22px] border border-white/10 bg-slate-950/40 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-[0.22em] text-slate-500">{formatDateTime(movement.created_at)}</p>
                      <h4 className="mt-1 text-sm font-medium text-slate-50">{movement.asset_label ?? "Movimentação"}</h4>
                    </div>
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
                      {movement.macro_copied ? "Macro copiada" : "Macro pendente"}
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{movement.justification}</p>
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">
                    <div className="rounded-[18px] border border-white/10 bg-white/5 p-3 text-xs text-slate-300">
                      Antes: {formatAssetStatus(movement.previous_status)} • {movement.previous_location ?? "Origem não informada"}
                    </div>
                    <div className="rounded-[18px] border border-white/10 bg-white/5 p-3 text-xs text-slate-300">
                      Depois: {formatAssetStatus(movement.new_status)} • {movement.new_location ?? "Destino não informado"}
                    </div>
                  </div>
                </article>
              ))
            ) : (
              <div className="rounded-[22px] border border-dashed border-white/15 bg-slate-950/35 p-5 text-slate-300">Nenhuma movimentação recente.</div>
            )}
          </div>

          <div className="mt-4 rounded-[22px] border border-white/10 bg-slate-950/40 p-4">
            <div className="flex items-center gap-3">
              <MapPin className="h-4 w-4 text-cyan-100" />
              <div>
                <p className="text-sm font-medium text-slate-50">Resumo operacional</p>
                <p className="text-sm leading-6 text-slate-400">
                  {recentMovements.length} evento(s) recentes • {recentResponsibleCount} responsável(is) distintos • {inUseAssets} em uso.
                </p>
              </div>
            </div>
          </div>
        </article>
      </section>
    </DonorPanelPageLayout>
  );
}
