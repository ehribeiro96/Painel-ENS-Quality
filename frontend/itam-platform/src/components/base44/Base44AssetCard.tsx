import type { ReactNode } from "react";

import { formatAssetStatus, formatDateTime } from "@/lib/format";
import type { Asset } from "@/lib/types";

import { Base44StatusBadge } from "./Base44StatusBadge";
import { Base44Surface } from "./Base44Surface";

export function Base44AssetCard({
  asset,
  actions,
  title,
  subtitle,
}: {
  asset: Asset;
  actions?: ReactNode;
  title?: ReactNode;
  subtitle?: ReactNode;
}) {
  const assetTitle = title ?? asset.hostname ?? asset.patrimony ?? asset.serial ?? asset.id;
  const assetSubtitle = subtitle ?? [asset.manufacturer, asset.model].filter(Boolean).join(" · ");

  return (
    <Base44Surface as="article" className="space-y-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Ativo</p>
          <h3 className="text-lg font-semibold text-slate-50">{assetTitle}</h3>
          {assetSubtitle ? <p className="text-sm text-slate-400">{assetSubtitle}</p> : null}
        </div>
        <Base44StatusBadge status={asset.status}>{formatAssetStatus(asset.status)}</Base44StatusBadge>
      </div>

      <dl className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
          <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Patrimônio</dt>
          <dd className="mt-1 text-sm text-slate-100">{asset.patrimony ?? "-"}</dd>
        </div>
        <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
          <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Usuário atual</dt>
          <dd className="mt-1 text-sm text-slate-100">{asset.current_user?.name ?? "Sem usuário"}</dd>
        </div>
        <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
          <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Localidade</dt>
          <dd className="mt-1 text-sm text-slate-100">{asset.location ?? "-"}</dd>
        </div>
        <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
          <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">Atualizado em</dt>
          <dd className="mt-1 text-sm text-slate-100">{formatDateTime(asset.updated_at)}</dd>
        </div>
      </dl>

      {asset.notes ? <p className="rounded-[22px] border border-white/10 bg-white/5 p-4 text-sm leading-6 text-slate-300">{asset.notes}</p> : null}

      {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
    </Base44Surface>
  );
}
