import type { ReactNode } from "react";

import { Base44Surface } from "./Base44Surface";

export type Base44InfoItem = {
  label: ReactNode;
  value: ReactNode;
  hint?: ReactNode;
};

export function Base44InfoGrid({
  title,
  items,
  columns = 2,
}: {
  title?: ReactNode;
  items: Base44InfoItem[];
  columns?: 1 | 2 | 3;
}) {
  return (
    <Base44Surface className={`base44-info-grid base44-info-grid-cols-${columns}`} as="section">
      {title ? <h2 className="base44-info-grid-title">{title}</h2> : null}
      <dl className="base44-info-grid-list">
        {items.map((item, index) => (
          <div className="base44-info-grid-item" key={`${String(item.label)}-${index}`}>
            <dt>{item.label}</dt>
            <dd>{item.value}</dd>
            {item.hint ? <p className="base44-info-grid-hint">{item.hint}</p> : null}
          </div>
        ))}
      </dl>
    </Base44Surface>
  );
}
