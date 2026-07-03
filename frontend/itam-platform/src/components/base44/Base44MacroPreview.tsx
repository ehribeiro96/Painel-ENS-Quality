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
    <Base44Surface as="section" className="space-y-4">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-2">
          <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Macro</p>
          <h3 className="text-lg font-semibold text-slate-50">{title}</h3>
          <p className="max-w-3xl text-sm leading-6 text-slate-400">{description}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {generationId ? <Base44StatusBadge status="auditavel">ID {generationId.slice(0, 8)}</Base44StatusBadge> : <Base44StatusBadge status="leitura">Sem geração</Base44StatusBadge>}
          {pendingFields.length ? <Base44StatusBadge status="warning">{pendingFields.length} pendente(s)</Base44StatusBadge> : <Base44StatusBadge status="success">Sem pendências</Base44StatusBadge>}
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <button className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-100 transition-colors hover:border-cyan-300/30 hover:bg-cyan-400/10" type="button" onClick={onGenerate}>
          <WandSparkles size={16} aria-hidden />
          Gerar preview
        </button>
        <button className="inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-4 py-2 text-sm font-medium text-slate-950 transition-colors hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60" type="button" onClick={onCopy} disabled={!hasRendered || !generationId}>
          <Copy size={16} aria-hidden />
          Copiar macro
        </button>
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
        <div className="rounded-[22px] border border-dashed border-white/15 bg-slate-950/35 p-4 text-sm text-slate-400">
          Preencha os campos obrigatórios e gere o preview para ver o conteúdo real da macro.
        </div>
      )}

      {copyStatus ? <p className="text-sm text-cyan-100">{copyStatus}</p> : null}
      {footer ? <div>{footer}</div> : null}
    </Base44Surface>
  );
}
