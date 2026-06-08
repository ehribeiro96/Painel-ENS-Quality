export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(date);
}

export function compactId(value: string | null | undefined) {
  if (!value) {
    return "-";
  }
  return value.length > 12 ? `${value.slice(0, 8)}...` : value;
}

const assetStatusLabels: Record<string, string> = {
  IN_USE: "Em uso",
  STOCK: "Em estoque",
  MAINTENANCE: "Em manutenção",
  DEFECTIVE: "Defeituoso",
  DISCARDED: "Baixado",
  RETIRED: "Baixado",
  RESERVED: "Reservado",
  CONFIG_PENDING: "Aguardando validação"
};

const importDecisionLabels: Record<string, string> = {
  CREATE: "Criar",
  SAFE_UPDATE: "Atualizar com segurança",
  SAFE_MERGE: "Mesclar com segurança",
  REVIEW_REQUIRED: "Revisar",
  CONFLICT: "Conflito",
  INVALID: "Inválida",
  SKIPPED: "Ignorada",
  SKIPPED_DUPLICATE_IN_FILE: "Duplicada no arquivo"
};

export function formatAssetStatus(value: string | null | undefined) {
  if (!value) return "-";
  return assetStatusLabels[value] ?? value;
}

export function formatImportDecision(value: string | null | undefined) {
  if (!value) return "-";
  return importDecisionLabels[value] ?? value;
}

export function formatTechnicalLabel(value: string | null | undefined) {
  if (!value) return "-";
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());
}
