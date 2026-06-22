import type { ReactNode } from "react";

import { formatDateTime } from "@/lib/format";
import type { User } from "@/lib/types";

import { Base44StatusBadge } from "./Base44StatusBadge";
import { Base44Surface } from "./Base44Surface";
import { Base44UserRoleBadge } from "./Base44UserRoleBadge";

function sourceLabel(source: string | null | undefined) {
  if (source === "legacy_ens_db") return "Legacy ENS DB";
  if (source === "manual") return "Manual";
  if (source === "entra_id" || source === "graph") return "Entra/Graph";
  return "Não informado";
}

function statusTone(status: string) {
  if (status === "ACTIVE") return "success";
  if (status === "INACTIVE") return "neutral";
  return "warning";
}

function statusLabel(status: string) {
  if (status === "ACTIVE") return "Ativo";
  if (status === "INACTIVE") return "Inativo";
  return "Afastado";
}

export function Base44UserCard({
  user,
  actions,
  title,
  subtitle,
}: {
  user: User;
  actions?: ReactNode;
  title?: ReactNode;
  subtitle?: ReactNode;
}) {
  return (
    <Base44Surface className="base44-user-card" as="article">
      <div className="base44-user-card-head">
        <div>
          <p className="base44-eyebrow">Colaborador</p>
          <h3>{title ?? user.name}</h3>
          <p className="base44-user-card-subtitle">{subtitle ?? user.email}</p>
        </div>
        <div className="base44-chip-row">
          <Base44UserRoleBadge role={user.role} />
          <Base44StatusBadge status={statusTone(user.status)}>{statusLabel(user.status)}</Base44StatusBadge>
        </div>
      </div>

      <dl className="base44-user-card-grid">
        <div>
          <dt>Identificador</dt>
          <dd>{user.email.split("@")[0] ?? "-"}</dd>
        </div>
        <div>
          <dt>Departamento</dt>
          <dd>{user.department ?? "-"}</dd>
        </div>
        <div>
          <dt>Unidade</dt>
          <dd>{user.business_unit ?? "-"}</dd>
        </div>
        <div>
          <dt>Fonte</dt>
          <dd>{sourceLabel(user.source)}</dd>
        </div>
        <div>
          <dt>Gestor</dt>
          <dd>{user.manager_name ?? "-"}</dd>
        </div>
        <div>
          <dt>Atualizado em</dt>
          <dd>{formatDateTime(user.updated_at)}</dd>
        </div>
      </dl>

      {actions ? <div className="base44-user-card-actions">{actions}</div> : null}
    </Base44Surface>
  );
}
