import { Check, Filter, LoaderCircle, RotateCcw } from "lucide-react";
import { StatusPill } from "./StatusPill";
import type { RagCollection } from "../lib/apoemaRagApi";
import type { RagCollectionId } from "../types";

function formatUpdatedAt(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "data indisponível";
  }
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

export function RagCollectionFilter({
  collections,
  selectedCollections,
  onChange,
  loading = false,
  error = null,
}: {
  collections: RagCollection[];
  selectedCollections: RagCollectionId[];
  onChange: (next: RagCollectionId[]) => void;
  loading?: boolean;
  error?: string | null;
}) {
  const allSelected = selectedCollections.length === 0;

  function toggleCollection(collectionId: RagCollectionId) {
    if (selectedCollections.includes(collectionId)) {
      onChange(selectedCollections.filter((item) => item !== collectionId));
      return;
    }
    onChange([...selectedCollections, collectionId]);
  }

  return (
    <div className="apoema-rag-filter-panel">
      <div className="apoema-rag-filter-head">
        <div>
          <StatusPill tone="info">
            <Filter size={14} />
            Collections
          </StatusPill>
          <h3>Escopo da busca</h3>
          <p>Selecione uma ou mais collections permitidas pelo backend. Sem coleção selecionada, a busca considera todas.</p>
        </div>
        {loading ? (
          <span className="apoema-rag-inline-status">
            <LoaderCircle size={14} className="is-spinning" />
            Carregando catálogo
          </span>
        ) : (
          <span className="apoema-rag-inline-status">
            <RotateCcw size={14} />
            {allSelected ? "Todas as collections" : `${selectedCollections.length} selecionada(s)`}
          </span>
        )}
      </div>

      {error ? (
        <div className="apoema-warning is-warning">
          <div>
            <strong>Catálogo indisponível</strong>
            <p>{error}</p>
          </div>
        </div>
      ) : null}

      <div className="apoema-rag-chip-grid" role="list" aria-label="Collections RAG">
        <button type="button" className={`apoema-rag-chip ${allSelected ? "is-active" : ""}`} onClick={() => onChange([])}>
          <Check size={14} />
          Todas
        </button>
        {collections.map((collection) => {
          const active = selectedCollections.includes(collection.id);
          return (
            <button key={collection.id} type="button" className={`apoema-rag-chip ${active ? "is-active" : ""}`} onClick={() => toggleCollection(collection.id)}>
              <strong>{collection.label}</strong>
              <span>{collection.document_count} docs</span>
              <small>{formatUpdatedAt(collection.updated_at)}</small>
            </button>
          );
        })}
      </div>

      <div className="apoema-rag-filter-foot">
        {collections.length > 0 ? (
          <small>
            Fontes permitidas: {collections
              .map((collection) => collection.tool_names.length > 0 ? `${collection.label} (${collection.tool_names.length} tools)` : collection.label)
              .join(" · ")}
          </small>
        ) : (
          <small>Catálogo vazio retornado pelo backend.</small>
        )}
      </div>
    </div>
  );
}
