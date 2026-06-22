import { Base44InfoGrid } from "./Base44InfoGrid";
import { Base44StatusBadge } from "./Base44StatusBadge";
import { Base44Surface } from "./Base44Surface";
import type { AuditLog } from "@/lib/types";
import { compactId, formatDateTime } from "@/lib/format";

function formatAuditLabel(value: string | null | undefined, fallback = "-") {
  if (!value) return fallback;
  return value
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .toLowerCase()
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function auditActionTone(action: string | null | undefined) {
  const normalized = (action ?? "").toUpperCase();
  if (normalized.includes("DELETE")) return "danger";
  if (normalized.includes("STATUS_CHANGE")) return "warning";
  if (normalized.includes("UPDATE") || normalized.includes("MOVE") || normalized.includes("IMPORT")) return "warning";
  if (normalized.includes("CREATE") || normalized.includes("LOGIN") || normalized.includes("SIGNATURE_GENERATE")) return "success";
  return "neutral";
}

function auditSourceTone(source: string | null | undefined) {
  const normalized = (source ?? "").toLowerCase();
  if (normalized.includes("auth") || normalized.includes("security")) return "warning";
  if (normalized.includes("legacy")) return "neutral";
  return "info";
}

function sanitizeAuditDetails(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(sanitizeAuditDetails);
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, item]) => {
        if (/password|token|secret|cookie|authorization|api[_-]?key|private[_-]?key/i.test(key)) {
          return [key, "[redigido]"];
        }
        return [key, sanitizeAuditDetails(item)];
      })
    );
  }
  if (typeof value === "string" && /bearer\s+|sk-|ghp_|akia/i.test(value)) {
    return "[redigido]";
  }
  return value;
}

export function Base44AuditEventCard({ item }: { item: AuditLog }) {
  const details = item.before || item.after
    ? JSON.stringify(
        {
          before: sanitizeAuditDetails(item.before),
          after: sanitizeAuditDetails(item.after),
        },
        null,
        2
      )
    : null;

  return (
    <Base44Surface className="base44-audit-event-card" as="article">
      <div className="base44-audit-event-card-head">
        <div>
          <p className="base44-eyebrow">Auditoria</p>
          <h3>{formatAuditLabel(item.action, "Ação não informada")}</h3>
          <p className="base44-audit-event-card-summary">
            {formatAuditLabel(item.entity, "Entidade não informada")}
            {item.entity_id ? <> · ID {compactId(item.entity_id)}</> : null}
          </p>
        </div>
        <div className="base44-chip-row">
          <Base44StatusBadge status={auditActionTone(item.action)} title={item.action ?? undefined}>
            {formatAuditLabel(item.action, "-")}
          </Base44StatusBadge>
          <Base44StatusBadge status={auditSourceTone(item.source)} title={item.source ?? undefined}>
            {formatAuditLabel(item.source, "Fonte não informada")}
          </Base44StatusBadge>
        </div>
      </div>

      <Base44InfoGrid
        columns={2}
        items={[
          { label: "Data/Hora", value: formatDateTime(item.created_at), hint: "Registro mais recente da amostra atual." },
          { label: "Usuário", value: item.actor_id ? compactId(item.actor_id) : "Usuário não informado", hint: item.actor_id ?? "Sem identificador de ator." },
          { label: "Entidade", value: formatAuditLabel(item.entity, "Entidade não informada") },
          { label: "Fonte", value: formatAuditLabel(item.source, "Fonte não informada") },
          { label: "Request ID", value: item.request_id ? compactId(item.request_id) : "Não informado" },
          { label: "Correlation ID", value: item.correlation_id ? compactId(item.correlation_id) : "Não informado" },
          { label: "Entity ID", value: item.entity_id ? compactId(item.entity_id) : "Não informado" },
          { label: "IP", value: item.ip_address ?? "Não informado" },
        ]}
      />

      {details ? (
        <details className="base44-audit-event-card-details">
          <summary>Ver before/after</summary>
          <pre className="base44-audit-event-card-pre">{details}</pre>
        </details>
      ) : (
        <p className="base44-audit-event-card-empty">Sem detalhe técnico registrado.</p>
      )}
    </Base44Surface>
  );
}
