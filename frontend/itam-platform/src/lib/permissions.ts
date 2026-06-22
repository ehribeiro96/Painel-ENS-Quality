import type { Role } from "./types";

const WRITE_ROLES: Role[] = ["ADMIN", "TECHNICIAN"];

export function canWriteOperationalData(role: Role | null | undefined) {
  return Boolean(role && WRITE_ROLES.includes(role));
}

export function canDeleteOperationalData(role: Role | null | undefined) {
  return role === "ADMIN";
}

export function accessModeLabel(role: Role | null | undefined) {
  if (!role) {
    return "Consulta";
  }
  return canWriteOperationalData(role) ? "Escrita habilitada" : "Somente leitura";
}
