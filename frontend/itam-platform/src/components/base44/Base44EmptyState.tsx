import type { ElementType, ReactNode } from "react";
import { PackageOpen } from "lucide-react";

import { Base44Surface } from "./Base44Surface";

export function Base44EmptyState({
  title = "Nenhum item encontrado",
  description = "Não há dados para exibir.",
  action,
  icon: Icon = PackageOpen,
}: {
  title?: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
  icon?: ElementType;
}) {
  return (
    <Base44Surface className="base44-empty-state base44-empty-shell" as="div">
      <div className="base44-empty-icon">
        <Icon size={18} aria-hidden="true" />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action ? <div className="base44-empty-action">{action}</div> : null}
    </Base44Surface>
  );
}
