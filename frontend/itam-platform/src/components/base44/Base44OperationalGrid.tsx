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
    <Base44Surface as="section" className="space-y-4">
      {title ? <h2 className="text-lg font-semibold text-slate-50">{title}</h2> : null}
      {description ? <p className="max-w-3xl text-sm leading-6 text-slate-400">{description}</p> : null}
      <div
        className={`grid gap-3 ${
          columns === 2 ? "md:grid-cols-2" : columns === 3 ? "md:grid-cols-2 xl:grid-cols-3" : "md:grid-cols-2 xl:grid-cols-4"
        }`}
      >
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
