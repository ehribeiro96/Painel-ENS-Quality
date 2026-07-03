import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

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
  const toneClass =
    variant === "is-online" || variant === "is-valid" || variant === "is-success"
      ? "border-emerald-300/20 bg-emerald-400/10 text-emerald-100"
      : variant === "is-warning" || variant === "is-pending"
        ? "border-amber-300/20 bg-amber-400/10 text-amber-100"
        : variant === "is-danger"
          ? "border-rose-300/20 bg-rose-500/10 text-rose-100"
          : variant === "is-audit"
            ? "border-cyan-300/20 bg-cyan-400/10 text-cyan-100"
            : "border-white/10 bg-white/5 text-slate-200";

  return (
    <span className={cn("inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium", toneClass)} title={title}>
      {children}
    </span>
  );
}
