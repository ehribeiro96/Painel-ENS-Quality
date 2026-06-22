import type { ReactNode } from "react";

import { Base44StatusBadge } from "./Base44StatusBadge";
import { Base44Surface } from "./Base44Surface";

export function Base44MacroPanel({
  eyebrow,
  title,
  description,
  status,
  actions,
  children,
}: {
  eyebrow?: ReactNode;
  title: ReactNode;
  description?: ReactNode;
  status?: ReactNode;
  actions?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <Base44Surface className="base44-macro-panel" as="section">
      <div className="base44-macro-panel-head">
        <div className="base44-macro-panel-copy">
          {eyebrow ? <p className="base44-eyebrow">{eyebrow}</p> : null}
          <div className="base44-macro-panel-titleline">
            <h2>{title}</h2>
            {status ? <Base44StatusBadge status="auditavel">{status}</Base44StatusBadge> : null}
          </div>
          {description ? <p className="base44-macro-panel-description">{description}</p> : null}
        </div>
        {actions ? <div className="base44-macro-panel-actions">{actions}</div> : null}
      </div>
      {children ? <div className="base44-macro-panel-body">{children}</div> : null}
    </Base44Surface>
  );
}
