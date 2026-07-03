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
    <ol className="space-y-4">
      {movements.map((movement) => {
        const macroLabel = movement.macro_generation_id
          ? `Macro ${compactId(movement.macro_generation_id)} · ${movement.macro_copied ? "copiada" : "não copiada"}`
          : "Macro não vinculada";
        return (
          <li key={movement.id} className="relative pl-5">
            <span className="absolute left-2 top-5 h-[calc(100%-2rem)] w-px bg-white/10" aria-hidden="true" />
            <span className="absolute left-1.5 top-6 h-3 w-3 rounded-full bg-cyan-300 shadow-[0_0_0_4px_rgba(34,211,238,0.12)]" aria-hidden="true" />

            <Base44Surface as="article" className="space-y-4">
              <header className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div className="space-y-1">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">{formatDateTime(movement.created_at)}</p>
                  <h3 className="text-lg font-semibold text-slate-50">{personLabel(movement.responsible_name, movement.responsible_id, "Responsável não informado")}</h3>
                  {movement.asset_label ? <p className="text-sm text-slate-400">Ativo: {movement.asset_label}</p> : null}
                </div>
                <Base44StatusBadge status={movement.new_status}>{formatAssetStatus(movement.new_status)}</Base44StatusBadge>
              </header>

              <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)]">
                <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
                  <span className="text-[11px] uppercase tracking-[0.22em] text-slate-500">Antes</span>
                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    {formatAssetStatus(movement.previous_status)} · {movement.previous_location ?? "Origem não informada"} · {personLabel(movement.previous_user_name, movement.previous_user_id, "Usuário não informado")}
                  </p>
                </div>
                <div className="flex items-center justify-center text-cyan-100">
                  <ArrowRight size={18} aria-hidden="true" />
                </div>
                <div className="rounded-[20px] border border-white/10 bg-slate-950/40 p-3">
                  <span className="text-[11px] uppercase tracking-[0.22em] text-slate-500">Depois</span>
                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    {formatAssetStatus(movement.new_status)} · {movement.new_location ?? "Destino não informado"} · {personLabel(movement.new_user_name, movement.new_user_id, "Usuário não informado")}
                  </p>
                </div>
              </div>

              <p className="rounded-[22px] border border-white/10 bg-white/5 p-4 text-sm leading-6 text-slate-300">{movement.justification}</p>
              <div className="flex flex-wrap gap-2 text-xs text-slate-400">
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">{macroLabel}</span>
                {movement.macro_copied ? (
                  <span className="inline-flex items-center gap-1 rounded-full border border-emerald-300/20 bg-emerald-400/10 px-3 py-1 text-emerald-100">
                    <CopyCheck size={14} aria-hidden="true" />
                    Copiada{movement.macro_copied_at ? ` em ${formatDateTime(movement.macro_copied_at)}` : ""}
                  </span>
                ) : null}
                {movement.notes ? <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">Observação: {movement.notes}</span> : null}
              </div>
            </Base44Surface>
          </li>
        );
      })}
    </ol>
  );
}
