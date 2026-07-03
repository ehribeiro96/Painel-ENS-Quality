import type { ReactNode } from "react";

export function Base44ShellAccent({
  title = "Painel ENS-Quality",
  subtitle = "Fonte visual Base44, contratos reais preservados",
  children,
}: {
  title?: ReactNode;
  subtitle?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-[24px] border border-white/10 bg-white/5 px-4 py-3">
      <div>
        <strong className="block text-sm font-semibold text-slate-50">{title}</strong>
        <p className="text-sm text-slate-400">{subtitle}</p>
      </div>
      {children ? <div>{children}</div> : null}
    </div>
  );
}
