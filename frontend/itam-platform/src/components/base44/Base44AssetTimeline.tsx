import { ArrowRight, ClipboardList, CopyCheck } from "lucide-react";

import { compactId, formatAssetStatus, formatDateTime } from "@/lib/format";
import type { Movement } from "@/lib/types";

import { Base44EmptyState } from "./Base44EmptyState";
import { Base44StatusBadge } from "./Base44StatusBadge";
import { Base44Surface } from "./Base44Surface";

function personLabel(name: string | null | undefined, id: string | null | undefined, fallback: string) {
  if (name) {
    return id ? `${name} · ID ${compactId(id)}` : name;
  }
  return id ? `ID ${compactId(id)}` : fallback;
}

export function Base44AssetTimeline({ movements }: { movements: Movement[] }) {
  if (movements.length === 0) {
    return (
      <Base44EmptyState
        title="Nenhuma movimentação registrada"
        description="O histórico operacional deste ativo aparecerá aqui assim que houver movimentações reais."
        icon={ClipboardList}
      />
    );
  }

  return (
    <ol className="base44-asset-timeline">
      {movements.map((movement) => {
        const macroLabel = movement.macro_generation_id
          ? `Macro ${compactId(movement.macro_generation_id)} · ${movement.macro_copied ? "copiada" : "não copiada"}`
          : "Macro não vinculada";
        return (
          <li key={movement.id}>
            <span className="base44-asset-timeline-rail" aria-hidden="true">
              <span className="base44-asset-timeline-dot" />
            </span>

            <Base44Surface className="base44-asset-timeline-card" as="article">
              <header className="base44-asset-timeline-header">
                <div>
                  <p className="base44-eyebrow">{formatDateTime(movement.created_at)}</p>
                  <h3>{personLabel(movement.responsible_name, movement.responsible_id, "Responsável não informado")}</h3>
                  {movement.asset_label ? <p className="base44-asset-timeline-subtitle">Ativo: {movement.asset_label}</p> : null}
                </div>
                <Base44StatusBadge status={movement.new_status}>{formatAssetStatus(movement.new_status)}</Base44StatusBadge>
              </header>

              <div className="base44-asset-timeline-flow">
                <div className="base44-asset-timeline-block">
                  <span className="base44-asset-timeline-label">Antes</span>
                  <p>
                    {formatAssetStatus(movement.previous_status)} · {movement.previous_location ?? "Origem não informada"} · {personLabel(movement.previous_user_name, movement.previous_user_id, "Usuário não informado")}
                  </p>
                </div>
                <ArrowRight size={18} aria-hidden="true" />
                <div className="base44-asset-timeline-block">
                  <span className="base44-asset-timeline-label">Depois</span>
                  <p>
                    {formatAssetStatus(movement.new_status)} · {movement.new_location ?? "Destino não informado"} · {personLabel(movement.new_user_name, movement.new_user_id, "Usuário não informado")}
                  </p>
                </div>
              </div>

              <p className="base44-asset-timeline-justification">{movement.justification}</p>
              <div className="base44-asset-timeline-meta">
                <span>{macroLabel}</span>
                {movement.macro_copied ? (
                  <span className="base44-asset-timeline-copied"><CopyCheck size={14} aria-hidden="true" /> Copiada{movement.macro_copied_at ? ` em ${formatDateTime(movement.macro_copied_at)}` : ""}</span>
                ) : null}
                {movement.notes ? <span>Observação: {movement.notes}</span> : null}
              </div>
            </Base44Surface>
          </li>
        );
      })}
    </ol>
  );
}
