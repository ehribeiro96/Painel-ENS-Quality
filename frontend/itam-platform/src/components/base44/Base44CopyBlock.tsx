import type { ReactNode } from "react";
import { Copy } from "lucide-react";

import { Base44Surface } from "./Base44Surface";

export function Base44CopyBlock({
  title,
  description,
  value,
  onCopy,
  copyLabel = "Copiar",
  emptyMessage = "Sem conteúdo disponível.",
  footer,
}: {
  title: ReactNode;
  description?: ReactNode;
  value: string;
  onCopy?: () => void;
  copyLabel?: string;
  emptyMessage?: ReactNode;
  footer?: ReactNode;
}) {
  const hasValue = Boolean(value);

  return (
    <Base44Surface className="b44-copy-block" as="article">
      <div className="b44-copy-block-head">
        <div>
          <h3>{title}</h3>
          {description ? <p className="b44-copy-description">{description}</p> : null}
        </div>
        {onCopy ? (
          <button className="button secondary" type="button" onClick={onCopy} disabled={!hasValue}>
            <Copy size={16} aria-hidden /> {copyLabel}
          </button>
        ) : null}
      </div>
      {hasValue ? <pre className="b44-copy-value">{value}</pre> : <div className="b44-copy-empty">{emptyMessage}</div>}
      {footer ? <div className="b44-copy-footer">{footer}</div> : null}
    </Base44Surface>
  );
}
