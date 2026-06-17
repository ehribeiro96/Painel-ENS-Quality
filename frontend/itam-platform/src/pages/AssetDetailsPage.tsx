import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, CheckCircle2, CircleAlert } from "lucide-react";
import { MoveAssetDialog } from "@/components/MoveAssetDialog";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDateTime } from "@/lib/format";
import type { Asset, Movement } from "@/lib/types";

function DetailItem({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <>
      <dt>{label}</dt>
      <dd>{value || "-"}</dd>
    </>
  );
}

function Timeline({ movements }: { movements: Movement[] }) {
  if (movements.length === 0) {
    return <div className="card muted-card">Nenhuma movimentacao registrada para este ativo.</div>;
  }

  return (
    <ol className="timeline" id="history">
      {movements.map((movement) => (
        <li key={movement.id}>
          <div className="timeline-dot" />
          <article className="timeline-card">
            <header>
              <strong>{formatDateTime(movement.created_at)}</strong>
              <span>Responsavel {movement.responsible_id?.slice(0, 8) ?? "-"}</span>
            </header>
            <div className="before-after">
              <div>
                <span className="metric-label">Antes</span>
                <p>{movement.previous_status} | {movement.previous_location ?? "sem local"} | {movement.previous_user_id?.slice(0, 8) ?? "sem usuario"}</p>
              </div>
              <ArrowRight size={18} aria-hidden />
              <div>
                <span className="metric-label">Depois</span>
                <p>{movement.new_status} | {movement.new_location ?? "sem local"} | {movement.new_user_id?.slice(0, 8) ?? "sem usuario"}</p>
              </div>
            </div>
            <p className="timeline-reason">{movement.justification}</p>
          </article>
        </li>
      ))}
    </ol>
  );
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
      <div className="page-title">
        <div>
          <h1>{asset?.hostname ?? asset?.patrimony ?? "Detalhe do ativo"}</h1>
          <p>Situacao atual, timeline operacional e auditoria do ativo.</p>
        </div>
        <button className="button" type="button" onClick={() => setMovingAsset(asset ?? null)} disabled={!asset}>Movimentar</button>
      </div>

      {assetQuery.isError ? <Alert tone="danger">Nao foi possivel carregar o ativo.</Alert> : null}
      {assetQuery.isLoading ? <LoadingBlock /> : null}

      {asset ? (
        <>
          <section className="status-strip" aria-label="Resumo operacional do ativo">
            <div><span>Status</span><strong className={`badge status-${asset.status.toLowerCase()}`}>{asset.status}</strong></div>
            <div><span>Local</span><strong>{asset.location ?? "-"}</strong></div>
            <div><span>Responsavel atual</span><strong>{asset.current_user?.name ?? "Sem usuario"}</strong></div>
            <div><span>Ultima movimentacao</span><strong>{lastMovement ? formatDateTime(lastMovement.created_at) : formatDateTime(asset.updated_at)}</strong></div>
          </section>

          {inconsistencies.length ? (
            <Alert tone="danger">
              <strong>Inconsistencias:</strong> {inconsistencies.join(" ")}
            </Alert>
          ) : (
            <Alert tone="success"><CheckCircle2 size={16} aria-hidden /> Situacao operacional consistente.</Alert>
          )}

          <section className="grid detail-grid">
            <article className="card">
              <h2>Identificacao</h2>
              <dl className="details">
                <DetailItem label="Hostname" value={asset.hostname} />
                <DetailItem label="Patrimonio" value={asset.patrimony} />
                <DetailItem label="Serial" value={asset.serial} />
                <DetailItem label="Tipo" value={asset.asset_type} />
              </dl>
            </article>
            <article className="card">
              <h2>Situacao atual</h2>
              <dl className="details">
                <DetailItem label="Status" value={asset.status} />
                <DetailItem label="Localidade" value={asset.location} />
                <DetailItem label="Usuario" value={asset.current_user?.name ?? "Sem usuario"} />
                <DetailItem label="E-mail" value={asset.current_user?.email} />
              </dl>
            </article>
            <article className="card">
              <h2>Informacoes tecnicas</h2>
              <dl className="details">
                <DetailItem label="Fabricante" value={asset.manufacturer} />
                <DetailItem label="Modelo" value={asset.model} />
                <DetailItem label="Sistema" value={asset.operating_system} />
                <DetailItem label="IP" value={asset.ip_address} />
                <DetailItem label="Ultimo login" value={asset.last_login} />
              </dl>
            </article>
            <article className="card">
              <h2>Auditoria rapida</h2>
              <dl className="details">
                <DetailItem label="Criado em" value={formatDateTime(asset.created_at)} />
                <DetailItem label="Atualizado em" value={formatDateTime(asset.updated_at)} />
                <dt>Auditoria</dt>
                <dd><Link to="/audit-logs">Consultar logs</Link></dd>
              </dl>
            </article>
          </section>

          <section>
            <div className="section-title">
              <h2><CircleAlert size={18} aria-hidden /> Timeline de movimentacoes</h2>
            </div>
            {historyQuery.isLoading ? <LoadingBlock label="Carregando historico..." /> : <Timeline movements={history} />}
          </section>
        </>
      ) : null}

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
