import { ArrowRight, ClipboardCopy, LoaderCircle, SearchX } from "lucide-react";
import { Link } from "react-router-dom";
import { StatusPill } from "./StatusPill";
import { RagDocumentCard } from "./RagDocumentCard";
import type { RagSearchResult } from "../lib/apoemaRagApi";

export function RagSearchResults({
  results,
  loading = false,
  error = null,
  query = "",
  toDocumentPath,
  onCopyReference,
}: {
  results: RagSearchResult[];
  loading?: boolean;
  error?: string | null;
  query?: string;
  toDocumentPath: (documentId: string) => string;
  onCopyReference?: (citation: string) => void;
}) {
  return (
    <section className="apoema-rag-results">
      <div className="apoema-section-head">
        <div>
          <StatusPill tone="warning">Busca read-only</StatusPill>
          <h2>Resultados</h2>
          <p>{query ? `Consulta: ${query}` : "Execute uma busca para ver resultados do backend."}</p>
        </div>
        <span>{loading ? "Carregando" : `${results.length} resultado(s)`}</span>
      </div>

      {error ? (
        <div className="apoema-warning is-warning">
          <SearchX size={16} />
          <div>
            <strong>Consulta indisponível</strong>
            <p>{error}</p>
          </div>
        </div>
      ) : null}

      {loading ? (
        <div className="apoema-empty-state">
          <LoaderCircle size={16} className="is-spinning" />
          <strong>Buscando no backend...</strong>
          <p>Sem fallback enganoso para 401, 403 ou 429.</p>
        </div>
      ) : null}

      {!loading && !error && results.length === 0 ? (
        <div className="apoema-empty-state">
          <strong>Nenhum resultado</strong>
          <p>Selecione uma collection ou refine a consulta para obter conteúdo do backend.</p>
        </div>
      ) : null}

      <div className="apoema-rag-result-list">
        {results.map((item) => (
          <RagDocumentCard
            key={item.document.document_id}
            document={item.document}
            score={item.score}
            matchedTerms={item.matched_terms}
            mode="search"
            actions={
              <div className="apoema-rag-document-actions">
                <Link className="apoema-secondary-button" to={toDocumentPath(item.document.document_id)}>
                  <ArrowRight size={14} />
                  Ver documento
                </Link>
                {onCopyReference ? (
                  <button
                    type="button"
                    className="apoema-ghost-button"
                    onClick={() => onCopyReference(item.document.citation)}
                  >
                    <ClipboardCopy size={14} />
                    Copiar referência
                  </button>
                ) : null}
              </div>
            }
          />
        ))}
      </div>
    </section>
  );
}
