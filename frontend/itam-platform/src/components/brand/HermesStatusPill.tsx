import type { HTMLAttributes } from "react";

type HermesStatusState =
  | "Online"
  | "Offline"
  | "Pendente"
  | "Em revisão"
  | "Validado"
  | "Conflito"
  | "Erro"
  | "Somente leitura"
  | "Auditável";

const stateTone: Record<HermesStatusState, "success" | "warning" | "danger" | "info" | "neutral"> = {
  Online: "success",
  Offline: "neutral",
  Pendente: "warning",
  "Em revisão": "info",
  Validado: "success",
  Conflito: "danger",
  Erro: "danger",
  "Somente leitura": "neutral",
  Auditável: "info"
};

const stateGlyph: Record<HermesStatusState, string> = {
  Online: "●",
  Offline: "○",
  Pendente: "…",
  "Em revisão": "↺",
  Validado: "✓",
  Conflito: "!",
  Erro: "×",
  "Somente leitura": "RO",
  Auditável: "AU"
};

export function HermesStatusPill({
  className,
  state = "Auditável",
  children,
  ...props
}: HTMLAttributes<HTMLSpanElement> & {
  children?: string;
  state?: HermesStatusState;
}) {
  const tone = stateTone[state];
  const label = children ?? state;

  return (
    <span
      className={["hermes-status-pill", `tone-${tone}`, className].filter(Boolean).join(" ")}
      data-state={state}
      {...props}
    >
      <span aria-hidden="true" className="hermes-status-glyph">
        {stateGlyph[state]}
      </span>
      <span>{label}</span>
    </span>
  );
}

export type { HermesStatusState };
