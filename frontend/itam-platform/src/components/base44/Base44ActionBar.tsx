import type { ReactNode } from "react";

import { Base44Surface } from "./Base44Surface";

export function Base44ActionBar({
  eyebrow,
  title,
  description,
  actions,
  children,
}: {
  eyebrow?: ReactNode;
  title?: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <Base44Surface className="base44-action-bar" as="section">
      <div className="base44-action-bar-copy">
        {eyebrow ? <p className="base44-eyebrow">{eyebrow}</p> : null}
        {title ? <h2>{title}</h2> : null}
        {description ? <p className="base44-action-bar-description">{description}</p> : null}
      </div>
      {actions ? <div className="base44-action-bar-actions">{actions}</div> : null}
      {children ? <div className="base44-action-bar-body">{children}</div> : null}
    </Base44Surface>
  );
}
