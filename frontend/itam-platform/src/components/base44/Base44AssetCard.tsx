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
    <Base44Surface className="base44-asset-card" as="article">
      <div className="base44-asset-card-head">
        <div>
          <p className="base44-eyebrow">Ativo</p>
          <h3>{assetTitle}</h3>
          {assetSubtitle ? <p className="base44-asset-card-subtitle">{assetSubtitle}</p> : null}
        </div>
        <Base44StatusBadge status={asset.status}>{formatAssetStatus(asset.status)}</Base44StatusBadge>
      </div>

      <dl className="base44-asset-card-grid">
        <div>
          <dt>Patrimônio</dt>
          <dd>{asset.patrimony ?? "-"}</dd>
        </div>
        <div>
          <dt>Usuário atual</dt>
          <dd>{asset.current_user?.name ?? "Sem usuário"}</dd>
        </div>
        <div>
          <dt>Localidade</dt>
          <dd>{asset.location ?? "-"}</dd>
        </div>
        <div>
          <dt>Atualizado em</dt>
          <dd>{formatDateTime(asset.updated_at)}</dd>
        </div>
      </dl>

      {asset.notes ? <p className="base44-asset-card-notes">{asset.notes}</p> : null}

      {actions ? <div className="base44-asset-card-actions">{actions}</div> : null}
    </Base44Surface>
  );
}
