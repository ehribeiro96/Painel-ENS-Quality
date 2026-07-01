import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ClipboardCopy, RefreshCcw, ShieldAlert } from "lucide-react";
import { RagDocumentCard } from "../components/RagDocumentCard";
import { StatusPill } from "../components/StatusPill";
import { ApoemaApiError } from "../types";
import { getRagDocument } from "../lib/apoemaRagApi";
import { useAuth } from "@/lib/auth";
import type { RagDocument } from "../lib/apoemaRagApi";

type DetailState = "loading" | "ready" | "unauthorized" | "forbidden" | "not_found" | "expired" | "unavailable" | "error";

type Banner = {
  tone: "warning" | "danger" | "success";
  title: string;
  message: string;
};

function describeError(error: unknown): Banner {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return { tone: "danger", title: "Sua sessão expirou", message: "Entre novamente para acessar este documento." };
    if (error.kind === "forbidden") return { tone: "danger", title: "Sem permissão", message: "Você não tem permissão para acessar este documento." };
    if (error.kind === "not_found") return { tone: "warning", title: "Documento não encontrado", message: "O backend não retornou este documento." };
    if (error.kind === "expired") return { tone: "warning", title: "Documento expirado", message: "O recurso não está mais disponível." };
    if (error.kind === "rate_limited") return { tone: "warning", title: "Limite atingido", message: "Tente novamente mais tarde." };
    if (error.kind === "network_unavailable") return { tone: "warning", title: "Backend indisponível", message: "Falha de rede ao consultar /api/v1/rag." };
    return { tone: "danger", title: "Erro da API", message: error.message };
  }
  return { tone: "danger", title: "Erro inesperado", message: "Operação não concluída." };
}

function stateFromError(error: unknown): DetailState {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return "unauthorized";
    if (error.kind === "forbidden") return "forbidden";
    if (error.kind === "not_found") return "not_found";
    if (error.kind === "expired") return "expired";
    if (error.kind === "network_unavailable") return "unavailable";
  }
  return "error";
}

export function RagDocumentPage() {
  const { documentId } = useParams();
  const { token } = useAuth();
  const [document, setDocument] = useState<RagDocument | null>(null);
  const [state, setState] = useState<DetailState>("loading");
  const [banner, setBanner] = useState<Banner | null>(null);

  async function reload(guard: () => boolean = () => true) {
    if (!documentId) {
      setDocument(null);
      setState("not_found");
      return;
    }
    setState("loading");
    setBanner(null);
    try {
      const result = await getRagDocument(documentId, token);
      if (!guard()) return;
      setDocument(result);
      setState("ready");
    } catch (error) {
      if (!guard()) return;
      setDocument(null);
      setState(stateFromError(error));
      setBanner(describeError(error));
    }
  }

  useEffect(() => {
    let active = true;
    void reload(() => active);
    return () => {
      active = false;
    };
  }, [documentId, token]);

  async function handleCopyReference() {
    if (!document) return;
    try {
      await navigator.clipboard.writeText(document.citation);
      setBanner({ tone: "success", title: "Referência copiada", message: "A referência segura do documento foi copiada para a área de transferência." });
    } catch {
      setBanner({ tone: "warning", title: "Não foi possível copiar", message: "Seu navegador bloqueou o acesso à área de transferência." });
    }
  }

  return (
    <div className="apoema-page apoema-rag-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="info">Documento RAG</StatusPill>
          <h1>Detalhe do documento</h1>
          <p>Metadata segura do backend RAG; sem path interno, sem storage path e sem token renderizado.</p>
        </div>
        <div className="apoema-rag-page-actions">
          <Link className="apoema-secondary-button" to="..">
            <ArrowLeft size={16} />
            Voltar para RAG
          </Link>
          <button type="button" className="apoema-secondary-button" onClick={() => void reload()} disabled={state === "loading"}>
            <RefreshCcw size={16} />
            Recarregar
          </button>
        </div>
      </section>

      {banner ? (
        <div className={`apoema-warning ${banner.tone === "danger" ? "is-danger" : "is-warning"}`}>
          <ShieldAlert size={16} />
          <div>
            <strong>{banner.title}</strong>
            <p>{banner.message}</p>
          </div>
        </div>
      ) : null}

      <section className="apoema-panel">
        <div className="apoema-section-head">
          <div>
            <StatusPill tone="warning">Read-only</StatusPill>
            <h2>Documento consultado pelo backend</h2>
          </div>
          <span>{document?.document_id ?? state}</span>
        </div>

        {state === "loading" ? <div className="apoema-empty-state">Carregando documento...</div> : null}
        {state === "unauthorized" ? (
          <div className="apoema-empty-state">
            <strong>Sua sessão expirou</strong>
            <p>Entre novamente para acessar este documento.</p>
          </div>
        ) : null}
        {state === "forbidden" ? (
          <div className="apoema-empty-state">
            <strong>Sem permissão</strong>
            <p>Você não tem permissão para acessar este documento.</p>
          </div>
        ) : null}
        {state === "not_found" ? (
          <div className="apoema-empty-state">
            <strong>Documento não encontrado</strong>
            <p>O documento não existe ou foi removido.</p>
          </div>
        ) : null}
        {state === "expired" ? (
          <div className="apoema-empty-state">
            <strong>Recurso expirado</strong>
            <p>O backend informou que este recurso não está mais disponível.</p>
          </div>
        ) : null}
        {state === "unavailable" ? (
          <div className="apoema-empty-state">
            <strong>Backend indisponível</strong>
            <p>Não foi possível consultar /api/v1/rag.</p>
          </div>
        ) : null}
        {state === "error" ? (
          <div className="apoema-empty-state">
            <strong>Erro operacional</strong>
            <p>Falha ao consultar o documento RAG.</p>
          </div>
        ) : null}

        {state === "ready" && document ? (
          <>
            <RagDocumentCard
              document={document}
              mode="detail"
              actions={
                <button type="button" className="apoema-ghost-button" onClick={() => void handleCopyReference()}>
                  <ClipboardCopy size={14} />
                  Copiar referência
                </button>
              }
            />
            <div className="apoema-rag-document-foot">
              <small>Collection: {document.collection}</small>
              <small>Documento consultado somente por backend; sem acesso direto ao storage.</small>
            </div>
          </>
        ) : null}
      </section>
    </div>
  );
}
