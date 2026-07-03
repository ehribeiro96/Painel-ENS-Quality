import type { ElementType, ReactNode } from "react";
import { PackageOpen } from "lucide-react";

import { Base44Surface } from "./Base44Surface";

export function Base44EmptyState({
  title = "Nenhum item encontrado",
  description = "Não há dados para exibir.",
  action,
  icon: Icon = PackageOpen,
}: {
  title?: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
  icon?: ElementType;
}) {
  return (
    <Base44Surface as="div" className="flex flex-col items-center justify-center gap-3 py-8 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-cyan-100">
        <Icon size={18} aria-hidden="true" />
      </div>
      <h3 className="text-base font-semibold text-slate-50">{title}</h3>
      <p className="max-w-lg text-sm leading-6 text-slate-400">{description}</p>
      {action ? <div>{action}</div> : null}
    </Base44Surface>
  );
}
