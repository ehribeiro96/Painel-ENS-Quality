import type { ReactNode } from "react";

export function SentinelSectionHeader({
  actions,
  children,
  className,
  chips,
  eyebrow,
  subtitle,
  title
}: {
  actions?: ReactNode;
  children?: ReactNode;
  className?: string;
  chips?: ReactNode;
  eyebrow?: ReactNode;
  subtitle?: ReactNode;
  title: ReactNode;
}) {
  return (
    <header className={["sentinel-section-header", className].filter(Boolean).join(" ")}>
      <div className="sentinel-section-header-copy">
        {eyebrow ? <span className="sentinel-section-eyebrow">{eyebrow}</span> : null}
        <div className="sentinel-section-title-row">
          <h1>{title}</h1>
          {chips ? <div className="sentinel-section-chips">{chips}</div> : null}
        </div>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>
      {actions || children ? <div className="sentinel-section-actions">{actions ?? children}</div> : null}
    </header>
  );
}
