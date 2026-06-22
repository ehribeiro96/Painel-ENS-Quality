import type { ReactNode } from "react";

const STATUS_VARIANTS: Record<string, string> = {
  online: "is-online",
  in_use: "is-online",
  em_uso: "is-online",
  stock: "is-valid",
  estoque: "is-valid",
  validado: "is-valid",
  maintenance: "is-warning",
  manutencao: "is-warning",
  reserved: "is-warning",
  reservado: "is-warning",
  config_pending: "is-pending",
  aguardando_validacao: "is-pending",
  auditavel: "is-audit",
  leitura: "is-muted",
  alerta: "is-warning",
  defective: "is-danger",
  defeituoso: "is-danger",
  discarded: "is-muted",
  baixado: "is-muted",
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
  const normalized = (status || String(children)).trim().toLowerCase().replaceAll(" ", "-").replaceAll("ç", "c");
  const variant = STATUS_VARIANTS[normalized] ?? "is-default";

  return (
    <span className={`base44-status-badge ${variant}`.trim()} title={title}>
      {children}
    </span>
  );
}
