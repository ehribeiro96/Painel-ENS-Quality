import type { ReactNode } from "react";

import { Base44Surface } from "./Base44Surface";

export function Base44ImportPanel({
  eyebrow,
  title,
  description,
  actions,
  children,
}: {
  eyebrow?: ReactNode;
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <Base44Surface className="base44-import-panel" as="section">
      <div className="base44-import-panel-head">
        <div className="base44-import-panel-copy">
          {eyebrow ? <p className="base44-eyebrow">{eyebrow}</p> : null}
          <h2>{title}</h2>
          {description ? <p className="base44-import-panel-description">{description}</p> : null}
        </div>
        {actions ? <div className="base44-import-panel-actions">{actions}</div> : null}
      </div>
      {children ? <div className="base44-import-panel-body">{children}</div> : null}
    </Base44Surface>
  );
}
