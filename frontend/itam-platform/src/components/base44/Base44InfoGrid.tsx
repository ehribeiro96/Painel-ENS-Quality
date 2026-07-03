import type { ReactNode } from "react";

import { Base44Surface } from "./Base44Surface";

export type Base44InfoItem = {
  label: ReactNode;
  value: ReactNode;
  hint?: ReactNode;
};

export function Base44InfoGrid({
  title,
  items,
  columns = 2,
}: {
  title?: ReactNode;
  items: Base44InfoItem[];
  columns?: 1 | 2 | 3 | 4;
}) {
  return (
    <Base44Surface as="section" className="space-y-4">
      {title ? <h2 className="text-lg font-semibold text-slate-50">{title}</h2> : null}
      <dl className={`grid gap-3 ${columns === 1 ? "md:grid-cols-1" : columns === 2 ? "md:grid-cols-2" : columns === 3 ? "md:grid-cols-2 xl:grid-cols-3" : "md:grid-cols-2 xl:grid-cols-4"}`}>
        {items.map((item, index) => (
          <div key={`${String(item.label)}-${index}`} className="rounded-[22px] border border-white/10 bg-slate-950/40 p-4">
            <dt className="text-xs uppercase tracking-[0.22em] text-slate-500">{item.label}</dt>
            <dd className="mt-2 text-lg font-semibold text-slate-50">{item.value}</dd>
            {item.hint ? <p className="mt-2 text-sm leading-6 text-slate-400">{item.hint}</p> : null}
          </div>
        ))}
      </dl>
    </Base44Surface>
  );
}
