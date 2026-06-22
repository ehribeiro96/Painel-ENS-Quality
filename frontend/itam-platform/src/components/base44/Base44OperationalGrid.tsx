import type { ElementType, ReactNode } from "react";

import { Base44MetricCard } from "./Base44MetricCard";
import { Base44Surface } from "./Base44Surface";

export type Base44OperationalItem = {
  title: ReactNode;
  value: ReactNode;
  description?: ReactNode;
  icon?: ElementType;
  accent?: ReactNode;
};

export function Base44OperationalGrid({
  title,
  description,
  items,
  columns = 4,
}: {
  title?: ReactNode;
  description?: ReactNode;
  items: Base44OperationalItem[];
  columns?: 2 | 3 | 4;
}) {
  return (
    <Base44Surface className={`base44-operational-grid base44-operational-grid-cols-${columns}`} as="section">
      {title ? <h2 className="base44-operational-grid-title">{title}</h2> : null}
      {description ? <p className="base44-operational-grid-description">{description}</p> : null}
      <div className="base44-operational-grid-list">
        {items.map((item, index) => (
          <Base44MetricCard
            key={`${String(item.title)}-${index}`}
            title={item.title}
            value={item.value}
            description={item.description}
            icon={item.icon}
            accent={item.accent}
          />
        ))}
      </div>
    </Base44Surface>
  );
}
