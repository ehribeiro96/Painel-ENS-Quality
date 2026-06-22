import type { ReactNode } from "react";

import { AuditReportIcon, HermesCoreIcon } from "@/components/icons/HermesIcons";

type AlertTone = "neutral" | "info" | "warning" | "danger" | "success";

export function Alert({ children, tone = "neutral" }: { children: ReactNode; tone?: AlertTone }) {
  const liveRole = tone === "neutral" || tone === "info" ? undefined : "alert";
  return <div className={`alert ${tone}`} role={liveRole}>{children}</div>;
}

export function AlertBlock({ children, tone = "neutral" }: { children: ReactNode; tone?: AlertTone }) {
  return <Alert tone={tone}>{children}</Alert>;
}

export function LoadingBlock({ label = "Carregando dados..." }: { label?: string }) {
  return (
    <div className="loading-state card muted-card sentinel-loading" aria-busy="true" aria-live="polite">
      <span className="loading-mark" aria-hidden="true">
        <HermesCoreIcon size={16} />
      </span>
      <span>{label}</span>
    </div>
  );
}

export function EmptyState({
  title = "Nenhum registro encontrado.",
  description,
  children
}: {
  title?: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <span className="empty-state-icon" aria-hidden="true">
        <AuditReportIcon size={20} />
      </span>
      <strong>{title}</strong>
      {description ? <p>{description}</p> : null}
      {children ? <div className="empty-state-actions">{children}</div> : null}
    </div>
  );
}
