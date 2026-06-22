import type { ReactNode } from "react";

export function StatusPill({
  tone,
  children
}: {
  tone: "success" | "warning" | "neutral" | "info";
  children: ReactNode;
}) {
  return <span className={`apoema-pill tone-${tone}`}>{children}</span>;
}
