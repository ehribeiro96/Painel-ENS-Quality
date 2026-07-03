import type { ReactNode } from "react";

import { Base44Surface } from "./Base44Surface";

export function Base44PageHeader({
  eyebrow,
  title,
  description,
  actions,
  breadcrumbs,
}: {
  eyebrow?: ReactNode;
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  breadcrumbs?: ReactNode;
}) {
  return (
    <Base44Surface as="header" className="space-y-4">
      {breadcrumbs ? <div className="text-xs uppercase tracking-[0.28em] text-slate-500">{breadcrumbs}</div> : null}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-3xl">
          {eyebrow ? <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">{eyebrow}</p> : null}
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-50 md:text-3xl">{title}</h1>
          {description ? <p className="mt-3 text-sm leading-6 text-slate-300 md:text-base">{description}</p> : null}
        </div>
        {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
      </div>
    </Base44Surface>
  );
}
