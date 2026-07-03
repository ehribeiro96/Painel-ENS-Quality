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
    <Base44Surface as="article" className="space-y-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Colaborador</p>
          <h3 className="text-lg font-semibold text-slate-50">{title ?? user.name}</h3>
          <p className="text-sm text-slate-400">{subtitle ?? user.email}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Base44UserRoleBadge role={user.role} />
          <Base44StatusBadge status={statusTone(user.status)}>{statusLabel(user.status)}</Base44StatusBadge>
        </div>
      </div>

      <dl className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
          <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Identificador</dt>
          <dd className="mt-1 text-sm text-slate-100">{user.email.split("@")[0] ?? "-"}</dd>
        </div>
        <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
          <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Departamento</dt>
          <dd className="mt-1 text-sm text-slate-100">{user.department ?? "-"}</dd>
        </div>
        <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
          <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Unidade</dt>
          <dd className="mt-1 text-sm text-slate-100">{user.business_unit ?? "-"}</dd>
        </div>
        <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
          <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Fonte</dt>
          <dd className="mt-1 text-sm text-slate-100">{sourceLabel(user.source)}</dd>
        </div>
        <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
          <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Gestor</dt>
          <dd className="mt-1 text-sm text-slate-100">{user.manager_name ?? "-"}</dd>
        </div>
        <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
          <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Atualizado em</dt>
          <dd className="mt-1 text-sm text-slate-100">{formatDateTime(user.updated_at)}</dd>
        </div>
      </dl>

      {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
    </Base44Surface>
  );
}
