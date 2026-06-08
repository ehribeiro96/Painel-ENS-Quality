import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { DataTable } from "@/components/DataTable";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Asset, User } from "@/lib/types";

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

  return (
    <>
      <div className="page-title">
        <div>
          <h1>Detalhe do usuario</h1>
          <p>Ativos vinculados, historico e dados corporativos de {user?.name ?? id}.</p>
        </div>
        <button className="button secondary" type="button">Gerar assinatura</button>
      </div>
      {error ? <Alert tone="danger">{error}</Alert> : null}
      {loading ? <LoadingBlock /> : null}
      <article className="card">
        <h2>Dados corporativos</h2>
        <dl className="details">
          <dt>E-mail</dt><dd>{user?.email ?? "-"}</dd>
          <dt>Cargo</dt><dd>{user?.job_title ?? "-"}</dd>
          <dt>Departamento</dt><dd>{user?.department ?? "-"}</dd>
          <dt>Unidade</dt><dd>{user?.business_unit ?? "-"}</dd>
          <dt>Perfil</dt><dd>{user?.role ?? "-"}</dd>
        </dl>
      </article>
      <DataTable
        items={assets}
        emptyMessage="Nenhum ativo vinculado a este usuario."
        columns={[
          { key: "hostname", label: "Hostname", render: (asset) => <Link to={`/assets/${asset.id}`}>{asset.hostname ?? "-"}</Link> },
          { key: "patrimony", label: "Patrimonio" },
          { key: "serial", label: "Serial" },
          { key: "status", label: "Status", render: (asset) => <span className="badge">{asset.status}</span> },
          { key: "location", label: "Localidade" }
        ]}
      />
    </>
  );
}
