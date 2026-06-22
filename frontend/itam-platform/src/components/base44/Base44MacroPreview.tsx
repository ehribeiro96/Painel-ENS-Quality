import type { ReactNode } from "react";
import { Copy, WandSparkles } from "lucide-react";

import { Base44CopyBlock } from "./Base44CopyBlock";
import { Base44StatusBadge } from "./Base44StatusBadge";
import { Base44Surface } from "./Base44Surface";

export function Base44MacroPreview({
  rendered,
  generationId,
  pendingFields,
  copyStatus,
  onGenerate,
  onCopy,
  title = "Preview da macro",
  description = "O texto gerado, os campos pendentes e o identificador de geração permanecem visíveis para auditoria do fluxo real.",
  footer,
}: {
  rendered: string;
  generationId: string | null;
  pendingFields: string[];
  copyStatus?: ReactNode;
  onGenerate: () => void;
  onCopy: () => void;
  title?: ReactNode;
  description?: ReactNode;
  footer?: ReactNode;
}) {
  const hasRendered = Boolean(rendered);

  return (
    <Base44Surface className="base44-macro-preview" as="section">
      <div className="base44-copy-block-head">
        <div>
          <p className="base44-eyebrow">Macro</p>
          <h3>{title}</h3>
          <p className="base44-macro-preview-description">{description}</p>
        </div>
        <div className="base44-chip-row">
          {generationId ? <Base44StatusBadge status="auditavel">ID {generationId.slice(0, 8)}</Base44StatusBadge> : <Base44StatusBadge status="leitura">Sem geração</Base44StatusBadge>}
          {pendingFields.length ? <Base44StatusBadge status="warning">{pendingFields.length} pendente(s)</Base44StatusBadge> : <Base44StatusBadge status="success">Sem pendências</Base44StatusBadge>}
        </div>
      </div>

      <div className="base44-macro-preview-actions">
        <button className="button secondary" type="button" onClick={onGenerate}><WandSparkles size={16} aria-hidden /> Gerar preview</button>
        <button className="button" type="button" onClick={onCopy} disabled={!hasRendered || !generationId}><Copy size={16} aria-hidden /> Copiar macro</button>
      </div>

      {hasRendered ? (
        <Base44CopyBlock
          title="Texto gerado"
          description="Este conteúdo vem diretamente do render real da macro selecionada."
          value={rendered}
          onCopy={onCopy}
          copyLabel="Copiar texto"
          emptyMessage="Sem conteúdo gerado."
        />
      ) : (
        <div className="base44-macro-preview-empty">
          <p>Preencha os campos obrigatórios e gere o preview para ver o conteúdo real da macro.</p>
        </div>
      )}

      {copyStatus ? <p className="base44-macro-preview-status">{copyStatus}</p> : null}
      {footer ? <div className="base44-macro-preview-footer">{footer}</div> : null}
    </Base44Surface>
  );
}
