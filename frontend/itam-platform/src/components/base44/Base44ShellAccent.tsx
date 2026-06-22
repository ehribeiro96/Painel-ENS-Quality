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
    <div className="base44-shell-accent">
      <div>
        <strong>{title}</strong>
        <p>{subtitle}</p>
      </div>
      {children ? <div className="base44-shell-accent-extra">{children}</div> : null}
    </div>
  );
}
