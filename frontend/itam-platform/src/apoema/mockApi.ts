import type { ApoemaAttachment } from "./types";

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

export function isSensitiveFilename(name: string) {
  return /\.(env|pem|key|pfx|p12|sqlite|db|sql|dump)$/i.test(name) || /token|secret|password/i.test(name);
}

export function attachmentWarning(attachments: ApoemaAttachment[]) {
  const sensitive = attachments.filter((file) => file.sensitive || isSensitiveFilename(file.name));
  if (sensitive.length === 0) {
    return null;
  }

  return {
    title: "Arquivo sensível detectado",
    description: sensitive.map((file) => file.name).join(", ")
  };
}

export async function mockApoemaResponse(prompt: string, attachments: ApoemaAttachment[], provider: string) {
  await sleep(700);

  const notes: string[] = [];
  if (attachments.length > 0) {
    notes.push(`Anexos recebidos: ${attachments.length}.`);
  }
  if (attachments.some((item) => item.sensitive || isSensitiveFilename(item.name))) {
    notes.push("Arquivos sensíveis foram sinalizados e não serão processados diretamente.");
  }

  const lead = prompt.trim().length > 0
    ? `Recebi seu pedido: "${prompt.trim()}".`
    : "Recebi uma solicitação vazia, então respondo com contexto operacional.";

  return [
    `${lead} O conector ${provider} está operando em modo mock para esta prévia do Apoema.`,
    "Posso consolidar ativos, sugerir prioridades e montar macros ou resumos operacionais sem sair da interface.",
    ...notes
  ].join(" ");
}
