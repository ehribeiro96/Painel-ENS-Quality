import { ArrowRight, RefreshCcw, WandSparkles } from "lucide-react";
import { StatusPill } from "./StatusPill";
import type { DesignerJobItem } from "../types";

function statusTone(status: DesignerJobItem["status"]) {
  switch (status) {
    case "completed":
      return "success";
    case "running":
      return "info";
    case "queued":
      return "neutral";
    case "cancelled":
    case "failed":
      return "warning";
    default:
      return "neutral";
  }
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "data indisponível";
  }
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

type Props = {
  items: DesignerJobItem[];
  busyItemId?: string | null;
  onAdjust: (item: DesignerJobItem) => void | Promise<void>;
  onRefreshUrl: (item: DesignerJobItem) => void | Promise<void>;
};

export function DesignerJobItems({ items, busyItemId = null, onAdjust, onRefreshUrl }: Props) {
  return (
    <section className="apoema-designer-job-items">
      <div className="apoema-section-head">
        <div>
          <StatusPill tone="info">Itens</StatusPill>
          <h2>Saída do job</h2>
          <p>Ajuste e refresh-url são os únicos atos permitidos nesta fase. Não existe download-url disponível na UI.</p>
        </div>
        <span>{items.length} item(ns)</span>
      </div>

      {items.length === 0 ? (
        <div className="apoema-empty-state">
          <strong>Sem itens</strong>
          <p>O backend não retornou itens para este job.</p>
        </div>
      ) : (
        <div className="apoema-designer-job-item-list">
          {items.map((item) => (
            <article key={item.item_id} className="apoema-designer-job-item">
              <div className="apoema-designer-job-item-head">
                <div>
                  <StatusPill tone={statusTone(item.status)}>{item.status}</StatusPill>
                  <strong>{item.title}</strong>
                </div>
                <span className="apoema-monospace">{item.item_id}</span>
              </div>

              <p>{item.result_note}</p>

              <dl className="apoema-designer-job-item-meta">
                <div>
                  <dt>Prompt</dt>
                  <dd>{item.prompt_preview}</dd>
                </div>
                <div>
                  <dt>Copy</dt>
                  <dd>{item.copy_preview || "—"}</dd>
                </div>
                <div>
                  <dt>Ajustes</dt>
                  <dd>{item.adjusted_count}</dd>
                </div>
                <div>
                  <dt>Refresh</dt>
                  <dd>{item.refresh_count}</dd>
                </div>
                <div>
                  <dt>Criado em</dt>
                  <dd>{formatDate(item.created_at)}</dd>
                </div>
                <div>
                  <dt>Atualizado em</dt>
                  <dd>{formatDate(item.updated_at)}</dd>
                </div>
              </dl>

              {item.error ? (
                <div className="apoema-warning is-warning">
                  <div>
                    <strong>Erro do item</strong>
                    <p>{item.error.message}</p>
                  </div>
                </div>
              ) : null}

              <div className="apoema-designer-job-item-actions">
                <button type="button" className="apoema-secondary-button" disabled={busyItemId === item.item_id} onClick={() => void onAdjust(item)}>
                  <WandSparkles size={16} />
                  Ajustar item
                </button>
                <button type="button" className="apoema-ghost-button" disabled={busyItemId === item.item_id} onClick={() => void onRefreshUrl(item)}>
                  <RefreshCcw size={16} />
                  Atualizar URL
                </button>
                <span className="apoema-designer-job-item-hint">
                  <ArrowRight size={14} />
                  download-url não está implementado nesta fase
                </span>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
