import { FileText, Link as LinkIcon, Tag } from "lucide-react";
import { StatusPill } from "./StatusPill";
import type { ReactNode } from "react";
import type { RagDocument } from "../lib/apoemaRagApi";

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "data indisponível";
  }
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function truncate(value: string, length: number) {
  if (value.length <= length) {
    return value;
  }
  return `${value.slice(0, length - 1).trimEnd()}…`;
}

export function RagDocumentCard({
  document,
  score,
  matchedTerms = [],
  mode,
  actions,
}: {
  document: RagDocument;
  score?: number;
  matchedTerms?: string[];
  mode: "search" | "detail";
  actions?: ReactNode;
}) {
  const excerpt = mode === "detail" ? document.content : truncate(document.summary, 220);

  return (
    <article className="apoema-rag-document-card">
      <div className="apoema-rag-document-head">
        <div>
          <StatusPill tone="info">
            <FileText size={14} />
            {document.collection}
          </StatusPill>
          <h3>{document.title}</h3>
        </div>
        {typeof score === "number" ? <StatusPill tone="warning">score {score}</StatusPill> : null}
      </div>

      <p className="apoema-rag-document-summary">{excerpt}</p>

      <dl className="apoema-rag-document-meta">
        <div>
          <dt>ID</dt>
          <dd className="apoema-monospace">{document.document_id}</dd>
        </div>
        <div>
          <dt>Atualizado em</dt>
          <dd>{formatDate(document.updated_at)}</dd>
        </div>
        <div>
          <dt>Citação</dt>
          <dd>{document.citation}</dd>
        </div>
        <div>
          <dt>Tags</dt>
          <dd>
            {document.tags.length > 0 ? (
              <span className="apoema-rag-tags">
                {document.tags.map((tag) => (
                  <span key={tag} className="apoema-rag-tag">
                    <Tag size={12} />
                    {tag}
                  </span>
                ))}
              </span>
            ) : (
              "Sem tags"
            )}
          </dd>
        </div>
      </dl>

      {matchedTerms.length > 0 ? (
        <div className="apoema-rag-matched-terms">
          <strong>Termos casados</strong>
          <p>{matchedTerms.join(" · ")}</p>
        </div>
      ) : null}

      <div className="apoema-rag-document-actions">
        <div className="apoema-rag-document-source">
          <LinkIcon size={14} />
          <span>{document.citation}</span>
        </div>
        {actions}
      </div>
    </article>
  );
}
