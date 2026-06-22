import type { ElementType, ReactNode } from "react";
import { CircleDot } from "lucide-react";

import { Base44Surface } from "./Base44Surface";

export function Base44MetricCard({
  title,
  value,
  description,
  icon: Icon = CircleDot,
  accent,
}: {
  title: ReactNode;
  value: ReactNode;
  description?: ReactNode;
  icon?: ElementType;
  accent?: ReactNode;
}) {
  return (
    <Base44Surface className="base44-metric-card" as="article">
      <div className="base44-metric-card-header">
        <span className="base44-metric-icon"><Icon size={18} aria-hidden="true" /></span>
        {accent ? <span className="base44-metric-accent">{accent}</span> : null}
      </div>
      <strong className="base44-metric-value">{value}</strong>
      <span className="base44-metric-label">{title}</span>
      {description ? <p className="base44-metric-description">{description}</p> : null}
    </Base44Surface>
  );
}
