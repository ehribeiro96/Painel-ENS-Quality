import type { ReactNode } from "react";
import { Copy } from "lucide-react";

import { Base44Surface } from "./Base44Surface";

export function Base44CopyBlock({
  title,
  description,
  value,
  onCopy,
  copyLabel = "Copiar",
  emptyMessage = "Sem conteúdo disponível.",
  footer,
}: {
  title: ReactNode;
  description?: ReactNode;
  value: string;
  onCopy?: () => void;
  copyLabel?: string;
  emptyMessage?: ReactNode;
  footer?: ReactNode;
}) {
  const hasValue = Boolean(value);

  return (
    <Base44Surface as="article" className="space-y-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-50">{title}</h3>
          {description ? <p className="mt-1 text-sm leading-6 text-slate-400">{description}</p> : null}
        </div>
        {onCopy ? (
          <button className="inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-4 py-2 text-sm font-medium text-slate-950 transition-colors hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60" type="button" onClick={onCopy} disabled={!hasValue}>
            <Copy size={16} aria-hidden />
            {copyLabel}
          </button>
        ) : null}
      </div>
      {hasValue ? (
        <pre className="max-h-[28rem] overflow-auto rounded-[22px] border border-white/10 bg-slate-950/85 p-4 text-sm leading-6 text-slate-200">{value}</pre>
      ) : (
        <div className="rounded-[22px] border border-dashed border-white/15 bg-slate-950/35 p-4 text-sm text-slate-400">{emptyMessage}</div>
      )}
      {footer ? <div>{footer}</div> : null}
    </Base44Surface>
  );
}
