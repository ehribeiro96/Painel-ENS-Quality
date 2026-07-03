import type { ElementType, ReactNode } from "react";
import { CircleDot } from "lucide-react";

import { Base44Surface } from "./Base44Surface";

export function Base44MetricCard({
  title,
  value,
  description,
  icon: Icon = CircleDot,
  accent,
}: {
  title: ReactNode;
  value: ReactNode;
  description?: ReactNode;
  icon?: ElementType;
  accent?: ReactNode;
}) {
  return (
    <Base44Surface as="article" className="space-y-3">
      <div className="flex items-start justify-between gap-3">
        <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-100 ring-1 ring-cyan-300/20">
          <Icon size={18} aria-hidden="true" />
        </span>
        {accent ? <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-medium text-slate-300">{accent}</span> : null}
      </div>
      <strong className="block text-2xl font-semibold tracking-tight text-slate-50">{value}</strong>
      <span className="block text-sm font-medium text-slate-200">{title}</span>
      {description ? <p className="text-sm leading-6 text-slate-400">{description}</p> : null}
    </Base44Surface>
  );
}
