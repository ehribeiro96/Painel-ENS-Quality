import type { ReactNode } from "react";

import { Base44Surface } from "./Base44Surface";

export function Base44FilterPanel({
  eyebrow,
  title,
  description,
  actions,
  chips,
  children,
}: {
  eyebrow?: ReactNode;
  title?: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  chips?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <Base44Surface className="base44-filter-panel" as="section">
      <div className="base44-filter-panel-head">
        <div className="base44-filter-panel-copy">
          {eyebrow ? <p className="base44-eyebrow">{eyebrow}</p> : null}
          {title ? <h2>{title}</h2> : null}
          {description ? <p className="base44-filter-panel-description">{description}</p> : null}
        </div>
        {actions ? <div className="base44-filter-panel-actions">{actions}</div> : null}
      </div>
      {chips ? <div className="base44-chip-row base44-filter-panel-chips">{chips}</div> : null}
      {children ? <div className="base44-filter-panel-body">{children}</div> : null}
    </Base44Surface>
  );
}
