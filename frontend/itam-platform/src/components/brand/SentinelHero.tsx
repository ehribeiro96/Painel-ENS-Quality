import type { ReactNode } from "react";

import { BrandMark } from "./BrandMark";
import { HermesCard } from "./HermesCard";

export function SentinelHero({
  actions,
  chips,
  children,
  description,
  eyebrow,
  subtitle,
  title
}: {
  actions?: ReactNode;
  chips?: ReactNode;
  children?: ReactNode;
  description?: ReactNode;
  eyebrow?: ReactNode;
  subtitle?: ReactNode;
  title: ReactNode;
}) {
  return (
    <HermesCard className="sentinel-hero" variant="active">
      <div className="sentinel-hero-grid">
        <div className="sentinel-hero-copy">
          <BrandMark subtitle={subtitle ? String(subtitle) : undefined} />
          <div className="sentinel-hero-text">
            {eyebrow ? <span className="sentinel-hero-eyebrow">{eyebrow}</span> : null}
            <h1>{title}</h1>
            {description ? <p>{description}</p> : null}
          </div>
          {chips ? <div className="sentinel-hero-chips">{chips}</div> : null}
        </div>
        <div className="sentinel-hero-aside">
          {actions ? <div className="sentinel-hero-actions">{actions}</div> : null}
          {children ? <div className="sentinel-hero-content">{children}</div> : null}
        </div>
      </div>
    </HermesCard>
  );
}
