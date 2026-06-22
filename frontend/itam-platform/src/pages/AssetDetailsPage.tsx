import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, CheckCircle2, CircleAlert, History } from "lucide-react";
import { Base44AssetCard } from "@/components/base44/Base44AssetCard";
import { Base44AssetTimeline } from "@/components/base44/Base44AssetTimeline";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44InfoGrid } from "@/components/base44/Base44InfoGrid";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
import { MoveAssetDialog } from "@/components/MoveAssetDialog";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { compactId, formatAssetStatus, formatDateTime } from "@/lib/format";
import type { Asset, Movement } from "@/lib/types";

function statusSentence(status: string | null | undefined) {
  return formatAssetStatus(status);
}

function assetSummary(asset: Asset | null | undefined) {
  return asset?.hostname ?? asset?.patrimony ?? asset?.serial ?? "Detalhe do ativo";
}

export function AssetDetailsPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [movingAsset, setMovingAsset] = useState<Asset | null>(null);

  const assetQuery = useQuery({
    queryKey: ["asset", id],
    enabled: Boolean(token && id),
    queryFn: () => api.asset(token as string, id as string)
  });

  const historyQuery = useQuery({
    queryKey: ["asset-history", id],
    enabled: Boolean(token && id),
    queryFn: () => api.assetHistory(token as string, id as string)
  });

  const usersQuery = useQuery({
    queryKey: ["users", "movement-select"],
    enabled: Boolean(token),
    queryFn: () => api.users(token as string, "?page_size=100")
  });

  const asset = assetQuery.data as Asset | undefined;
  const history = (historyQuery.data ?? []) as Movement[];
  const lastMovement = history[0];
  const inconsistencies = useMemo(() => {
    const items: string[] = [];
    if (asset?.status === "IN_USE" && !asset.current_user_id) items.push("Ativo em uso sem usuario vinculado.");
    if (asset?.status === "STOCK" && asset.current_user_id) items.push("Ativo em estoque com usuario vinculado.");
    if (!asset?.serial && !asset?.patrimony && !asset?.hostname) items.push("Ativo sem identidade operacional.");
    return items;
  }, [asset]);

  return (
    <>
      <Base44PageHeader
        eyebrow="Registro operacional"
        title={assetSummary(asset)}
        description="Situação atual, timeline operacional e auditoria do ativo com fluxo real da API."
        breadcrumbs={[
          <Link key="dashboard" to="/">Dashboard</Link>,
          <span key="sep-1">/</span>,
          <Link key="assets" to="/assets">Ativos</Link>,
          <span key="sep-2">/</span>,
          <span key="detail">Detalhe do ativo</span>
        ]}
        actions={
          <button className="button" type="button" onClick={() => setMovingAsset(asset ?? null)} disabled={!asset}>
            Movimentar
          </button>
        }
      />

      {assetQuery.isError ? <Alert tone="danger">Não foi possível carregar o ativo.</Alert> : null}
      {assetQuery.isLoading ? <LoadingBlock /> : null}

      {asset ? (
        <>
          <section className="base44-asset-detail-hero">
            <Base44AssetCard
              asset={asset}
              title={asset.hostname ?? asset.patrimony ?? asset.serial ?? asset.id}
              subtitle={[asset.asset_type, asset.manufacturer, asset.model].filter(Boolean).join(" · ")}
              actions={
                <div className="row-action-group base44-asset-card-actions-inline">
                  <button className="mini-button" type="button" onClick={() => setMovingAsset(asset)}>
                    <ArrowRight size={15} aria-hidden="true" /> Movimentar
                  </button>
                  <Link className="mini-button" to="#history">
                    <History size={15} aria-hidden="true" /> Histórico
                  </Link>
                </div>
              }
            />

            <Base44Surface className="base44-asset-detail-strip" as="aside">
              <div>
                <span>Status</span>
                <Base44StatusBadge status={asset.status}>{statusSentence(asset.status)}</Base44StatusBadge>
              </div>
              <div>
                <span>Local</span>
                <strong>{asset.location ?? "-"}</strong>
              </div>
              <div>
                <span>Responsável atual</span>
                <strong>{asset.current_user?.name ?? "Sem usuário"}</strong>
              </div>
              <div>
                <span>Última movimentação</span>
                <strong>{lastMovement ? formatDateTime(lastMovement.created_at) : formatDateTime(asset.updated_at)}</strong>
              </div>
            </Base44Surface>
          </section>

          {inconsistencies.length ? (
            <Alert tone="danger">
              <strong>Inconsistências:</strong> {inconsistencies.join(" ")}
            </Alert>
          ) : (
            <Alert tone="success"><CheckCircle2 size={16} aria-hidden /> Situação operacional consistente.</Alert>
          )}

          <section className="grid detail-grid base44-asset-detail-grid">
            <Base44InfoGrid
              title="Identificação"
              columns={2}
              items={[
                { label: "Hostname", value: asset.hostname ?? "-" },
                { label: "Patrimônio", value: asset.patrimony ?? "-" },
                { label: "Serial", value: asset.serial ?? "-" },
                { label: "Tipo", value: asset.asset_type },
              ]}
            />
            <Base44InfoGrid
              title="Situação atual"
              columns={2}
              items={[
                { label: "Status", value: <Base44StatusBadge status={asset.status}>{formatAssetStatus(asset.status)}</Base44StatusBadge> },
                { label: "Localidade", value: asset.location ?? "-" },
                { label: "Usuário", value: asset.current_user?.name ?? "Sem usuário" },
                { label: "E-mail", value: asset.current_user?.email ?? "-" },
              ]}
            />
            <Base44InfoGrid
              title="Informações técnicas"
              columns={2}
              items={[
                { label: "Fabricante", value: asset.manufacturer ?? "-" },
                { label: "Modelo", value: asset.model ?? "-" },
                { label: "Sistema", value: asset.operating_system ?? "-" },
                { label: "IP", value: asset.ip_address ?? "-" },
                { label: "Último login", value: asset.last_login ?? "-" },
                { label: "Criado em", value: formatDateTime(asset.created_at) },
              ]}
            />
            <Base44InfoGrid
              title="Auditoria rápida"
              columns={2}
              items={[
                { label: "Atualizado em", value: formatDateTime(asset.updated_at) },
                { label: "Responsável atual", value: asset.current_user?.name ?? "Sem usuário" },
                { label: "Resumo", value: asset.notes ?? "Sem observações" },
                {
                  label: "Auditoria",
                  value: <Link to="/audit-logs">Consultar logs</Link>,
                  hint: compactId(asset.id),
                },
              ]}
            />
          </section>

          <Base44Surface className="base44-asset-history-shell" as="section" id="history">
            <div className="base44-form-header">
              <div>
                <p className="base44-eyebrow">Histórico operacional</p>
                <h2><CircleAlert size={18} aria-hidden="true" /> Timeline de movimentações</h2>
                <p>O histórico abaixo preserva rastreabilidade, geração de macro e status da cópia.</p>
              </div>
            </div>
            {historyQuery.isLoading ? <LoadingBlock label="Carregando histórico..." /> : <Base44AssetTimeline movements={history} />}
          </Base44Surface>
        </>
      ) : (
        !assetQuery.isLoading ? (
          <Base44EmptyState
            title="Ativo não encontrado"
            description="O registro solicitado não existe ou não está acessível com o seu perfil."
            action={<Link className="button secondary" to="/assets">Voltar para ativos</Link>}
          />
        ) : null
      )}

      <MoveAssetDialog
        asset={movingAsset}
        token={token ?? ""}
        users={usersQuery.data}
        onClose={() => setMovingAsset(null)}
        onMoved={() => {
          void queryClient.invalidateQueries({ queryKey: ["asset", id] });
          void queryClient.invalidateQueries({ queryKey: ["asset-history", id] });
          void queryClient.invalidateQueries({ queryKey: ["assets"] });
        }}
      />
    </>
  );
}
