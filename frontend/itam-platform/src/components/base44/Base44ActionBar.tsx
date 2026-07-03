import type { ReactNode } from "react";

import { Base44Surface } from "./Base44Surface";

export function Base44ActionBar({
  eyebrow,
  title,
  description,
  actions,
  children,
}: {
  eyebrow?: ReactNode;
  title?: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <Base44Surface as="section" className="space-y-4">
      <div className="space-y-2">
        {eyebrow ? <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">{eyebrow}</p> : null}
        {title ? <h2 className="text-lg font-semibold text-slate-50">{title}</h2> : null}
        {description ? <p className="max-w-3xl text-sm leading-6 text-slate-400">{description}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
      {children ? <div>{children}</div> : null}
    </Base44Surface>
  );
}
