import type { Role } from "@/lib/types";

import { Base44StatusBadge } from "./Base44StatusBadge";

const ROLE_LABELS: Record<Role, string> = {
  ADMIN: "Admin",
  TECHNICIAN: "Técnico",
  VIEWER: "Consulta",
  MANAGER: "Gestor"
};

function roleTone(role: Role) {
  if (role === "ADMIN") return "danger";
  if (role === "TECHNICIAN") return "info";
  if (role === "MANAGER") return "warning";
  return "neutral";
}

export function Base44UserRoleBadge({ role }: { role: Role }) {
  return <Base44StatusBadge status={roleTone(role)}>{ROLE_LABELS[role] ?? role}</Base44StatusBadge>;
}
