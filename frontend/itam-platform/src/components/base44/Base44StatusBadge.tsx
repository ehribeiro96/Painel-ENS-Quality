import type { ReactNode } from "react";

const STATUS_VARIANTS: Record<string, string> = {
  online: "is-online",
  auditavel: "is-audit",
  validado: "is-valid",
  pendente: "is-pending",
  leitura: "is-muted",
  alerta: "is-warning",
  danger: "is-danger",
  sucesso: "is-success",
};

export function Base44StatusBadge({
  children,
  status,
  title,
}: {
  children: ReactNode;
  status?: string;
  title?: string;
}) {
  const key = (status || String(children)).trim().toLowerCase().replaceAll(" ", "-").replaceAll("ç", "c");
  const variant = STATUS_VARIANTS[key] ?? "is-default";

  return (
    <span className={`base44-status-badge ${variant}`.trim()} title={title}>
      {children}
    </span>
  );
}
