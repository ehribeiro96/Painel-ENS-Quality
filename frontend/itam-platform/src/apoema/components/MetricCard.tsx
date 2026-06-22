import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { StatusPill } from "./StatusPill";
import type { ApoemaMetric } from "../types";

export function MetricCard({ metric }: { metric: ApoemaMetric }) {
  const icon =
    metric.tone === "positive" ? (
      <ArrowUpRight size={16} />
    ) : metric.tone === "alert" ? (
      <ArrowDownRight size={16} />
    ) : (
      <Minus size={16} />
    );

  return (
    <article className="apoema-metric-card">
      <div className="apoema-metric-top">
        <span>{metric.label}</span>
        <StatusPill tone={metric.tone === "positive" ? "success" : metric.tone === "alert" ? "warning" : "neutral"}>
          {icon}
          {metric.delta}
        </StatusPill>
      </div>
      <strong>{metric.value}</strong>
      <p>{metric.hint}</p>
    </article>
  );
}
