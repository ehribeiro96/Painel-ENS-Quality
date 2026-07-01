import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Download, Eye, RotateCcw, Search, ShieldAlert, Trash2, UploadCloud } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { ApoemaApiError } from "../types";
import { deleteArtifact, getArtifactDownloadUrl, listArtifacts, uploadArtifact } from "../lib/apoemaArtifactsApi";
import { useAuth } from "@/lib/auth";
import type { ApoemaArtifact } from "../lib/apoemaArtifactsApi";

type PageState = "loading" | "ready" | "empty" | "unauthorized" | "forbidden" | "unavailable" | "error";

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

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "data indisponível";
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function describeError(error: unknown): Banner {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") {
      return { tone: "danger", title: "Sessão expirada", message: "Faça login novamente para acessar os artefatos." };
    }
    if (error.kind === "forbidden") {
      return { tone: "danger", title: "Sem permissão", message: "Seu perfil não tem permissão para esta operação." };
    }
    if (error.kind === "not_found") {
      return { tone: "warning", title: "Artefato não encontrado", message: "O registro solicitado não existe mais ou não está acessível." };
    }
    if (error.kind === "expired") {
      return { tone: "warning", title: "Link expirado", message: "Gere um novo download pelo backend para continuar." };
    }
    if (error.kind === "validation_error") {
      return { tone: "warning", title: "Arquivo recusado", message: "O backend recusou tipo, extensão, nome ou tamanho do arquivo." };
    }
    if (error.kind === "network_unavailable") {
      return { tone: "warning", title: "Backend indisponível", message: "Não foi possível alcançar /api/v1/artifacts." };
    }
    return { tone: "danger", title: "Erro da API", message: error.message };
  }
  return { tone: "danger", title: "Erro inesperado", message: "Operação não concluída." };
}

function stateFromError(error: unknown): PageState {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return "unauthorized";
    if (error.kind === "forbidden") return "forbidden";
    if (error.kind === "network_unavailable") return "unavailable";
  }
  return "error";
}

function matchesQuery(artifact: ApoemaArtifact, query: string) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return true;
  return [artifact.filename, artifact.content_type, artifact.id, artifact.sha256].some((value) => value.toLowerCase().includes(normalized));
}

export function ArtifactsPage() {
  const { token } = useAuth();
  const [artifacts, setArtifacts] = useState<ApoemaArtifact[]>([]);
  const [state, setState] = useState<PageState>("loading");
  const [banner, setBanner] = useState<Banner | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [query, setQuery] = useState("");

  async function reload(guard: () => boolean = () => true) {
    setState("loading");
    setBanner(null);
    try {
      const result = await listArtifacts(token);
      if (!guard()) return;
      setArtifacts(result.items);
      setState(result.items.length > 0 ? "ready" : "empty");
    } catch (error) {
      if (!guard()) return;
      setArtifacts([]);
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
  }, [token]);

  async function handleUpload(file: File | null, resetInput: () => void) {
    if (!file || uploading) return;
    setUploading(true);
    setBanner(null);
    try {
      await uploadArtifact(file, token);
      setBanner({ tone: "success", title: "Upload registrado", message: "Arquivo enviado para storage privado gerenciado pelo backend." });
      await reload();
    } catch (error) {
      setBanner(describeError(error));
      setState(stateFromError(error));
    } finally {
      setUploading(false);
      resetInput();
    }
  }

  async function handleDownload(artifactId: string) {
    setBusyId(artifactId);
    setBanner(null);
    try {
      const result = await getArtifactDownloadUrl(artifactId, token);
      window.open(result.url, "_blank", "noopener,noreferrer");
      setBanner({ tone: "success", title: "Download iniciado", message: "URL temporária gerada pelo backend e aberta sem exibir o valor na interface." });
    } catch (error) {
      setBanner(describeError(error));
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(artifact: ApoemaArtifact) {
    const confirmed = window.confirm(`Excluir "${artifact.filename}"? Esta ação é irreversível e será auditada pelo backend.`);
    if (!confirmed) return;
    setBusyId(artifact.id);
    setBanner(null);
    try {
      await deleteArtifact(artifact.id, token);
      setBanner({ tone: "success", title: "Artefato excluído", message: "Exclusão registrada pelo backend com auditoria." });
      await reload();
    } catch (error) {
      setBanner(describeError(error));
    } finally {
      setBusyId(null);
    }
  }

  const filteredArtifacts = useMemo(() => artifacts.filter((artifact) => matchesQuery(artifact, query)), [artifacts, query]);
  const showTable = state === "ready" || artifacts.length > 0;

  return (
    <div className="apoema-page apoema-stub-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="success">Backend</StatusPill>
          <h1>Artefatos</h1>
          <p>Backend Artifact Storage — arquivos gerenciados pelo backend com storage privado backend-owned.</p>
        </div>
        <label className="apoema-file-action">
          <UploadCloud size={16} />
          {uploading ? "Enviando..." : "Enviar arquivo"}
          <input
            type="file"
            disabled={uploading}
            onChange={(event) => {
              const input = event.currentTarget;
              void handleUpload(event.target.files?.[0] ?? null, () => {
                input.value = "";
              });
            }}
          />
        </label>
      </section>

      <div className="apoema-warning is-warning">
        <ShieldAlert size={16} />
        <div>
          <strong>Storage privado backend-owned</strong>
          <p>A interface chama somente /api/v1/artifacts, não acessa storage direto, não expõe caminho interno e não exibe URL temporária completa; a URL não é registrada em console.</p>
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
            <StatusPill tone="info">Artifacts API</StatusPill>
            <h2>Artefatos registrados</h2>
          </div>
          <button type="button" className="apoema-secondary-button" onClick={() => void reload()}>
            <RotateCcw size={16} />
            Recarregar
          </button>
        </div>

        <div className="apoema-filter-bar">
          <label className="apoema-search">
            <Search size={16} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar por nome, MIME, ID ou SHA-256" />
          </label>
        </div>

        {state === "loading" && <div className="apoema-empty-state">Carregando artefatos...</div>}
        {state === "empty" && <div className="apoema-empty-state"><strong>Nenhum artefato</strong><p>Envie um arquivo para registrar o primeiro artefato seguro.</p></div>}
        {state === "unauthorized" && <div className="apoema-empty-state"><strong>Sessão expirada</strong><p>Entre novamente para acessar a biblioteca.</p></div>}
        {state === "forbidden" && <div className="apoema-empty-state"><strong>Sem permissão</strong><p>Seu perfil não pode listar os artefatos disponíveis.</p></div>}
        {state === "unavailable" && <div className="apoema-empty-state"><strong>Backend indisponível</strong><p>A UI não cria fallback mock quando /api/v1 não responde.</p></div>}
        {state === "error" && <div className="apoema-empty-state"><strong>Erro operacional</strong><p>Falha ao consultar o backend de artefatos.</p></div>}

        {showTable && filteredArtifacts.length === 0 && state !== "loading" ? (
          <div className="apoema-empty-state"><strong>Nenhum resultado</strong><p>Ajuste a busca para ver os artefatos carregados.</p></div>
        ) : null}

        {showTable && filteredArtifacts.length > 0 && (
          <div className="apoema-table-wrap">
            <table className="apoema-table apoema-stub-table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Tipo</th>
                  <th>Tamanho</th>
                  <th>Origem/status</th>
                  <th>Criado em</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {filteredArtifacts.map((artifact) => (
                  <tr key={artifact.id}>
                    <td><strong>{artifact.filename}</strong><span>ID {artifact.id.slice(0, 8)}</span></td>
                    <td>{artifact.content_type}</td>
                    <td>{formatBytes(artifact.size_bytes)}</td>
                    <td><strong>Backend Artifact</strong><span>{artifact.deleted_at ? "Excluído" : "Ativo"}</span></td>
                    <td>{formatDate(artifact.created_at)}</td>
                    <td>
                      <div className="apoema-row-actions">
                        <Link className="apoema-secondary-button" to={artifact.id}>
                          <Eye size={14} />
                          Detalhes
                        </Link>
                        <button type="button" className="apoema-secondary-button" disabled={busyId === artifact.id} onClick={() => void handleDownload(artifact.id)}>
                          <Download size={14} />
                          Download
                        </button>
                        <button type="button" className="apoema-ghost-button" disabled={busyId === artifact.id} onClick={() => void handleDelete(artifact)}>
                          <Trash2 size={14} />
                          Excluir
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
