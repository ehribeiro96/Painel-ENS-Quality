import type { ReactNode } from "react";

import { Base44Surface } from "./Base44Surface";

export function Base44PageHeader({
  eyebrow,
  title,
  description,
  actions,
  breadcrumbs,
}: {
  eyebrow?: ReactNode;
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  breadcrumbs?: ReactNode;
}) {
  return (
    <Base44Surface className="base44-page-header" as="header">
      {breadcrumbs ? <div className="base44-page-breadcrumbs">{breadcrumbs}</div> : null}
      <div className="base44-page-header-row">
        <div className="base44-page-titleblock">
          {eyebrow ? <p className="base44-eyebrow">{eyebrow}</p> : null}
          <h1>{title}</h1>
          {description ? <p className="base44-page-description">{description}</p> : null}
        </div>
        {actions ? <div className="base44-page-actions">{actions}</div> : null}
      </div>
    </Base44Surface>
  );
}
