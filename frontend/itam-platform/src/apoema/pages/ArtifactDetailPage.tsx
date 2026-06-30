import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Download, RotateCcw, ShieldAlert, Trash2 } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { ApoemaApiError } from "../types";
import { deleteArtifact, getArtifact, getArtifactDownloadUrl } from "../lib/apoemaArtifactsApi";
import { useAuth } from "@/lib/auth";
import type { ApoemaArtifact } from "../lib/apoemaArtifactsApi";

type DetailState = "loading" | "ready" | "unauthorized" | "forbidden" | "not_found" | "unavailable" | "error";

type Banner = {
  tone: "warning" | "danger" | "success";
  title: string;
  message: string;
};

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(kb >= 10 ? 0 : 1)} KB`;
  const mb = kb / 1024;
  return `${mb.toFixed(mb >= 10 ? 0 : 1)} MB`;
}

function formatDate(value: string | null) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "data indisponível";
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function describeError(error: unknown): Banner {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return { tone: "danger", title: "Sua sessão expirou", message: "Entre novamente para acessar este artefato." };
    if (error.kind === "forbidden") return { tone: "danger", title: "Sem permissão", message: "Você não tem permissão para acessar este artefato." };
    if (error.kind === "not_found") return { tone: "warning", title: "Artefato não encontrado", message: "O artefato não existe ou foi removido." };
    if (error.kind === "expired") return { tone: "warning", title: "Link expirado", message: "Gere um novo download pelo backend." };
    if (error.kind === "network_unavailable") return { tone: "warning", title: "Backend indisponível", message: "Não foi possível alcançar /api/v1/artifacts." };
    return { tone: "danger", title: "Erro da API", message: error.message };
  }
  return { tone: "danger", title: "Erro inesperado", message: "Operação não concluída." };
}

function stateFromError(error: unknown): DetailState {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return "unauthorized";
    if (error.kind === "forbidden") return "forbidden";
    if (error.kind === "not_found") return "not_found";
    if (error.kind === "network_unavailable") return "unavailable";
  }
  return "error";
}

export function ArtifactDetailPage() {
  const { artifactId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const [artifact, setArtifact] = useState<ApoemaArtifact | null>(null);
  const [state, setState] = useState<DetailState>("loading");
  const [banner, setBanner] = useState<Banner | null>(null);
  const [busy, setBusy] = useState(false);

  async function reload(guard: () => boolean = () => true) {
    if (!artifactId) {
      setState("not_found");
      setArtifact(null);
      return;
    }
    setState("loading");
    setBanner(null);
    try {
      const result = await getArtifact(artifactId, token);
      if (!guard()) return;
      setArtifact(result);
      setState("ready");
    } catch (error) {
      if (!guard()) return;
      setArtifact(null);
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
  }, [artifactId, token]);

  async function handleDownload() {
    if (!artifactId) return;
    setBusy(true);
    setBanner(null);
    try {
      const result = await getArtifactDownloadUrl(artifactId, token);
      window.open(result.url, "_blank", "noopener,noreferrer");
      setBanner({ tone: "success", title: "Download iniciado", message: "URL temporária gerada pelo backend e aberta sem exibir o valor na interface." });
    } catch (error) {
      setBanner(describeError(error));
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete() {
    if (!artifactId || !artifact) return;
    const confirmed = window.confirm(`Excluir "${artifact.filename}"? Esta ação é irreversível e será auditada pelo backend.`);
    if (!confirmed) return;
    setBusy(true);
    setBanner(null);
    try {
      await deleteArtifact(artifactId, token);
      setBanner({ tone: "success", title: "Artefato excluído", message: "Exclusão registrada pelo backend com auditoria." });
      navigate("../artifacts", { replace: true });
    } catch (error) {
      setBanner(describeError(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="apoema-page apoema-stub-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="success">Backend</StatusPill>
          <h1>{artifact?.filename ?? "Detalhe do artefato"}</h1>
          <p>Metadata segura do artefato; sem caminho interno, sem storage direto e sem token temporário visível.</p>
        </div>
        <Link className="apoema-secondary-button" to="../artifacts">
          <ArrowLeft size={16} />
          Voltar
        </Link>
      </section>

      <div className="apoema-warning is-warning">
        <ShieldAlert size={16} />
        <div>
          <strong>Download mediado pelo backend</strong>
          <p>O link temporário é solicitado sob demanda e aberto sem renderizar o valor completo na tela.</p>
        </div>
      </div>

      {banner && (
        <div className={`apoema-warning ${banner.tone === "danger" ? "is-danger" : "is-warning"}`}>
          <ShieldAlert size={16} />
          <div>
            <strong>{banner.title}</strong>
            <p>{banner.message}</p>
          </div>
        </div>
      )}

      <section className="apoema-panel">
        <div className="apoema-section-head">
          <div>
            <StatusPill tone="info">Metadata</StatusPill>
            <h2>Registro do artefato</h2>
          </div>
          <button type="button" className="apoema-secondary-button" onClick={() => void reload()} disabled={state === "loading"}>
            <RotateCcw size={16} />
            Recarregar
          </button>
        </div>

        {state === "loading" && <div className="apoema-empty-state">Carregando artefato...</div>}
        {state === "unauthorized" && <div className="apoema-empty-state"><strong>Sua sessão expirou</strong><p>Faça login novamente para acessar este artefato.</p></div>}
        {state === "forbidden" && <div className="apoema-empty-state"><strong>Sem permissão</strong><p>Você não tem permissão para acessar este artefato.</p></div>}
        {state === "not_found" && <div className="apoema-empty-state"><strong>Artefato não encontrado</strong><p>O registro não existe ou foi removido.</p></div>}
        {state === "unavailable" && <div className="apoema-empty-state"><strong>Backend indisponível</strong><p>Não foi possível consultar /api/v1/artifacts.</p></div>}
        {state === "error" && <div className="apoema-empty-state"><strong>Erro operacional</strong><p>Falha ao consultar o detalhe do artefato.</p></div>}

        {artifact && state === "ready" ? (
          <>
            <dl className="apoema-detail-grid apoema-artifact-detail-grid">
              <div><dt>Nome</dt><dd>{artifact.filename}</dd></div>
              <div><dt>Tipo MIME</dt><dd>{artifact.content_type}</dd></div>
              <div><dt>Tamanho</dt><dd>{formatBytes(artifact.size_bytes)}</dd></div>
              <div><dt>ID</dt><dd>{artifact.id}</dd></div>
              <div><dt>Proprietário</dt><dd>{artifact.owner_user_id}</dd></div>
              <div><dt>Downloads</dt><dd>{artifact.download_count}</dd></div>
              <div><dt>Criado em</dt><dd>{formatDate(artifact.created_at)}</dd></div>
              <div><dt>Atualizado em</dt><dd>{formatDate(artifact.updated_at)}</dd></div>
              <div><dt>Checksum SHA-256</dt><dd className="apoema-monospace">{artifact.sha256}</dd></div>
              <div><dt>Status</dt><dd>{artifact.deleted_at ? `Excluído em ${formatDate(artifact.deleted_at)}` : "Ativo"}</dd></div>
            </dl>

            <div className="apoema-artifact-actions">
              <button type="button" className="apoema-primary-button" onClick={() => void handleDownload()} disabled={busy}>
                <Download size={16} />
                Download
              </button>
              <button type="button" className="apoema-ghost-button" onClick={() => void handleDelete()} disabled={busy}>
                <Trash2 size={16} />
                Excluir com confirmação
              </button>
            </div>
          </>
        ) : null}
      </section>
    </div>
  );
}
