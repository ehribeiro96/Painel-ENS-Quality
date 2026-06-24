import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { DataTable } from "@/components/DataTable";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44OperationalGrid } from "@/components/base44/Base44OperationalGrid";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
import { Base44UserCard } from "@/components/base44/Base44UserCard";
import { Base44UserRoleBadge } from "@/components/base44/Base44UserRoleBadge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Asset, User } from "@/lib/types";

function statusLabel(status: string | null | undefined) {
  if (status === "ACTIVE") return "Ativo";
  if (status === "INACTIVE") return "Inativo";
  if (status === "ON_LEAVE") return "Afastado";
  return "-";
}

export function UserDetailsPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !id) {
      return;
    }
    setLoading(true);
    Promise.all([api.user(token, id), api.userAssets(token, id)])
      .then(([userData, assetData]) => {
        setUser(userData);
        setAssets(assetData);
        setError(null);
      })
      .catch(() => setError("Nao foi possivel carregar o usuario."))
      .finally(() => setLoading(false));
  }, [id, token]);

  const summaryItems = useMemo(
    () => [
      { title: "Ativos vinculados", value: assets.length, description: "Itens associados ao colaborador na API real.", accent: "Histórico" },
      { title: "Perfil", value: user?.role ?? "-", description: "Papel operacional do colaborador.", accent: user ? <Base44UserRoleBadge role={user.role} /> : "Sem perfil" },
      { title: "Situação", value: statusLabel(user?.status), description: "Estado atual do cadastro.", accent: user?.status ?? "Sem dados" },
      { title: "Fonte", value: user?.source ?? "-", description: "Origem do registro do usuário.", accent: user?.source ?? "Sem origem" }
    ],
    [assets.length, user]
  );

  return (
    <div className="base44-user-page">
      <Base44PageHeader
        eyebrow="Apoema Usuários"
        title="Detalhe do usuário"
        description={`Ativos vinculados, histórico e dados corporativos de ${user?.name ?? id}.`}
        actions={
          <>
            <Link className="button secondary" to="/apoema/users">Voltar</Link>
            <Link className="button secondary" to="/apoema/signatures">Gerar assinatura</Link>
          </>
        }
        breadcrumbs={(
          <div className="base44-breadcrumbs">
            <span>Apoema</span>
            <span>/</span>
            <span>Usuários</span>
            <span>/</span>
            <span>Detalhe</span>
          </div>
        )}
      />

      <Base44OperationalGrid
        title="Resumo do colaborador"
        description="A leitura abaixo é alimentada pelos contratos reais de usuário e vínculo."
        columns={4}
        items={summaryItems}
      />

      {error ? <Alert tone="danger">{error}</Alert> : null}
      {loading ? <LoadingBlock /> : null}

      {user ? (
        <Base44Surface className="base44-user-detail-shell" as="section">
          <Base44UserCard
            user={user}
            actions={
              <div className="base44-chip-row">
                <Base44StatusBadge status="auditavel">{statusLabel(user.status)}</Base44StatusBadge>
                <Base44StatusBadge status="leitura">{user.email}</Base44StatusBadge>
              </div>
            }
          />

          <div className="base44-user-detail-grid">
            <Base44Surface className="base44-user-detail-card" as="article">
              <p className="base44-eyebrow">Dados corporativos</p>
              <h2>Perfil e contexto</h2>
              <dl className="details">
                <dt>E-mail</dt><dd>{user.email}</dd>
                <dt>Cargo</dt><dd>{user.job_title ?? "-"}</dd>
                <dt>Departamento</dt><dd>{user.department ?? "-"}</dd>
                <dt>Unidade</dt><dd>{user.business_unit ?? "-"}</dd>
                <dt>Gestor</dt><dd>{user.manager_name ?? "-"}</dd>
                <dt>Perfil</dt><dd>{user.role}</dd>
              </dl>
            </Base44Surface>

            <Base44Surface className="base44-user-detail-card" as="article">
              <p className="base44-eyebrow">Ativos vinculados</p>
              <h2>Relações operacionais</h2>
              <p className="base44-operation-panel-description">A lista abaixo usa a relação real do colaborador com os ativos vinculados.</p>
              <DataTable
                items={assets}
                emptyMessage="Nenhum ativo vinculado a este usuario."
                emptyTitle="Nenhum ativo vinculado"
                emptyDescription="Quando houver relações registradas, elas aparecerão nesta tabela."
                emptyActions={<Link className="button secondary" to="/apoema/assets">Abrir inventário</Link>}
                columns={[
                  { key: "hostname", label: "Hostname", render: (asset) => <Link to={`/apoema/assets/${asset.id}`}>{asset.hostname ?? "-"}</Link> },
                  { key: "patrimony", label: "Patrimônio" },
                  { key: "serial", label: "Serial" },
                  { key: "status", label: "Status", render: (asset) => <span className="badge">{asset.status}</span> },
                  { key: "location", label: "Localidade" }
                ]}
              />
            </Base44Surface>
          </div>
        </Base44Surface>
      ) : null}

      {user === null && !loading && !error ? (
        <Base44EmptyState
          title="Usuário indisponível"
          description="Não foi possível carregar os dados do colaborador."
          action={<Link className="button secondary" to="/apoema/users">Voltar</Link>}
        />
      ) : null}
    </div>
  );
}
