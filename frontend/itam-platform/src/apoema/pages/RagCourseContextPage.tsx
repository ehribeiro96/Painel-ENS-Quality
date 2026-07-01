import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, RefreshCcw, ShieldAlert } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { ApoemaApiError } from "../types";
import { getRagCourseContext } from "../lib/apoemaRagApi";
import { useAuth } from "@/lib/auth";
import type { RagCourseContext } from "../lib/apoemaRagApi";

type DetailState = "loading" | "ready" | "unauthorized" | "forbidden" | "not_found" | "expired" | "unavailable" | "error";

type Banner = {
  tone: "warning" | "danger" | "success";
  title: string;
  message: string;
};

function describeError(error: unknown): Banner {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return { tone: "danger", title: "Sua sessão expirou", message: "Entre novamente para acessar o contexto do curso." };
    if (error.kind === "forbidden") return { tone: "danger", title: "Sem permissão", message: "Você não tem permissão para acessar este contexto." };
    if (error.kind === "not_found") return { tone: "warning", title: "Contexto não encontrado", message: "O backend não retornou este contexto de curso." };
    if (error.kind === "expired") return { tone: "warning", title: "Recurso expirado", message: "O contexto não está mais disponível." };
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

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "data indisponível";
  }
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

export function RagCourseContextPage() {
  const { courseId } = useParams();
  const { token } = useAuth();
  const [courseContext, setCourseContext] = useState<RagCourseContext | null>(null);
  const [state, setState] = useState<DetailState>("loading");
  const [banner, setBanner] = useState<Banner | null>(null);

  async function reload(guard: () => boolean = () => true) {
    if (!courseId) {
      setCourseContext(null);
      setState("not_found");
      return;
    }
    setState("loading");
    setBanner(null);
    try {
      const result = await getRagCourseContext(courseId, token);
      if (!guard()) return;
      setCourseContext(result);
      setState("ready");
    } catch (error) {
      if (!guard()) return;
      setCourseContext(null);
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
  }, [courseId, token]);

  return (
    <div className="apoema-page apoema-rag-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="info">Contexto RAG</StatusPill>
          <h1>Contexto de curso</h1>
          <p>Bloco read-only trazido pelo backend RAG sem inventar dados fora do contrato.</p>
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
            <h2>{courseId ?? "Contexto do curso"}</h2>
          </div>
          <span>{state}</span>
        </div>

        {state === "loading" ? <div className="apoema-empty-state">Carregando contexto...</div> : null}
        {state === "unauthorized" ? (
          <div className="apoema-empty-state">
            <strong>Sua sessão expirou</strong>
            <p>Entre novamente para acessar este contexto.</p>
          </div>
        ) : null}
        {state === "forbidden" ? (
          <div className="apoema-empty-state">
            <strong>Sem permissão</strong>
            <p>Você não tem permissão para acessar este contexto.</p>
          </div>
        ) : null}
        {state === "not_found" ? (
          <div className="apoema-empty-state">
            <strong>Contexto não encontrado</strong>
            <p>O curso não foi localizado no backend.</p>
          </div>
        ) : null}
        {state === "expired" ? (
          <div className="apoema-empty-state">
            <strong>Recurso expirado</strong>
            <p>O backend informou que este contexto não está mais disponível.</p>
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
            <p>Falha ao consultar o contexto do curso.</p>
          </div>
        ) : null}

        {state === "ready" && courseContext ? (
          <div className="apoema-rag-course-context">
            <div className="apoema-rag-document-card">
              <StatusPill tone="info">Collection {courseContext.collection}</StatusPill>
              <h3>{courseContext.title}</h3>
              <p>{courseContext.summary}</p>
              <dl className="apoema-rag-document-meta">
                <div>
                  <dt>Course ID</dt>
                  <dd className="apoema-monospace">{courseContext.course_id}</dd>
                </div>
                <div>
                  <dt>Público</dt>
                  <dd>{courseContext.audience}</dd>
                </div>
                <div>
                  <dt>Atualizado em</dt>
                  <dd>{formatDate(courseContext.updated_at)}</dd>
                </div>
              </dl>
            </div>

            <div className="apoema-rag-sidecard">
              <strong>Documentos-chave</strong>
              <ul className="apoema-rag-bullet-list">
                {courseContext.key_documents.map((documentId) => (
                  <li key={documentId} className="apoema-monospace">
                    {documentId}
                  </li>
                ))}
              </ul>
              <strong>Recomendações</strong>
              <ul className="apoema-rag-bullet-list">
                {courseContext.recommendations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        ) : null}
      </section>
    </div>
  );
}
