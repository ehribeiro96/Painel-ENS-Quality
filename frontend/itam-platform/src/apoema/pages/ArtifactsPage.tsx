import { useEffect, useState } from "react";
import { Copy, Download, RotateCcw, ShieldAlert, Trash2, UploadCloud } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import { ApoemaApiError } from "../types";
import { deleteArtifact, getArtifactDownloadUrl, listArtifacts, uploadArtifact } from "../lib/apoemaArtifactsApi";
import { useAuth } from "@/lib/auth";
import type { ApoemaArtifact } from "../lib/apoemaArtifactsApi";

type PageState = "loading" | "ready" | "empty" | "unauthorized" | "unavailable" | "error";

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
      return { tone: "danger", title: "Sessão necessária", message: "Faça login novamente para acessar os artefatos." };
    }
    if (error.kind === "forbidden") {
      return { tone: "danger", title: "Sem permissão", message: "Seu perfil não tem permissão para esta operação." };
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
    if (error.kind === "auth_required" || error.kind === "forbidden") return "unauthorized";
    if (error.kind === "network_unavailable") return "unavailable";
  }
  return "error";
}

export function ArtifactsPage() {
  const { token } = useAuth();
  const [artifacts, setArtifacts] = useState<ApoemaArtifact[]>([]);
  const [state, setState] = useState<PageState>("loading");
  const [banner, setBanner] = useState<Banner | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<{ artifactId: string; url: string; expiresAt: string } | null>(null);

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

  async function handleUpload(file: File | null) {
    if (!file || uploading) return;
    setUploading(true);
    setBanner(null);
    try {
      await uploadArtifact(file, token);
      setBanner({ tone: "success", title: "Upload registrado", message: "Arquivo enviado para storage seguro backend-owned." });
      await reload();
    } catch (error) {
      setBanner(describeError(error));
      setState(stateFromError(error));
    } finally {
      setUploading(false);
    }
  }

  async function handleDownloadUrl(artifactId: string) {
    setBusyId(artifactId);
    setBanner(null);
    try {
      const result = await getArtifactDownloadUrl(artifactId, token);
      setDownloadUrl({ artifactId, url: result.url, expiresAt: result.expires_at });
      setBanner({ tone: "success", title: "Link assinado obtido", message: "URL mantida apenas na sessão do navegador; não é registrada em console nem relatório." });
    } catch (error) {
      setBanner(describeError(error));
    } finally {
      setBusyId(null);
    }
  }

  async function copyCurrentUrl() {
    if (!downloadUrl) return;
    await navigator.clipboard.writeText(downloadUrl.url);
    setBanner({ tone: "success", title: "URL copiada", message: "URL assinada copiada sem impressão em console." });
  }

  async function handleDelete(artifactId: string) {
    setBusyId(artifactId);
    setBanner(null);
    try {
      await deleteArtifact(artifactId, token);
      setDownloadUrl((current) => (current?.artifactId === artifactId ? null : current));
      setBanner({ tone: "success", title: "Artefato excluído", message: "Exclusão registrada pelo backend com auditoria." });
      await reload();
    } catch (error) {
      setBanner(describeError(error));
    } finally {
      setBusyId(null);
    }
  }

  const showTable = state === "ready" || artifacts.length > 0;

  return (
    <div className="apoema-page apoema-stub-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="success">Backend</StatusPill>
          <h1>Biblioteca de Artefatos</h1>
          <p>Backend Artifact Storage — storage seguro backend-owned com upload, listagem, link assinado e exclusão controlados por /api/v1.</p>
        </div>
        <label className="apoema-file-action">
          <UploadCloud size={16} />
          {uploading ? "Enviando..." : "Enviar arquivo"}
          <input type="file" disabled={uploading} onChange={(event) => void handleUpload(event.target.files?.[0] ?? null)} />
        </label>
      </section>

      <div className="apoema-warning is-warning">
        <ShieldAlert size={16} />
        <div>
          <strong>Storage seguro backend-owned</strong>
          <p>Arquivos são armazenados no backend; a interface não expõe caminho interno, conteúdo sensível ou URL assinada em logs.</p>
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

        {state === "loading" && <div className="apoema-empty-state">Carregando artefatos...</div>}
        {state === "empty" && <div className="apoema-empty-state"><strong>Nenhum artefato</strong><p>Envie um arquivo para validar o adapter de storage.</p></div>}
        {state === "unauthorized" && <div className="apoema-empty-state"><strong>Sessão/permissão necessária</strong><p>O backend recusou a chamada autenticada.</p></div>}
        {state === "unavailable" && <div className="apoema-empty-state"><strong>Backend indisponível</strong><p>A UI não cria mock falso quando /api/v1 não responde.</p></div>}
        {state === "error" && <div className="apoema-empty-state"><strong>Erro operacional</strong><p>Falha ao consultar o backend de artefatos.</p></div>}

        {showTable && (
          <div className="apoema-table-wrap">
            <table className="apoema-table apoema-stub-table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Tipo</th>
                  <th>Tamanho</th>
                  <th>Status/data</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {artifacts.map((artifact) => (
                  <tr key={artifact.id}>
                    <td><strong>{artifact.filename}</strong><span>ID {artifact.id.slice(0, 8)}</span></td>
                    <td>{artifact.content_type}</td>
                    <td>{formatBytes(artifact.size_bytes)}</td>
                    <td><strong>ativo</strong><span>{formatDate(artifact.created_at)}</span></td>
                    <td>
                      <div className="apoema-row-actions">
                        <button type="button" className="apoema-secondary-button" disabled={busyId === artifact.id} onClick={() => void handleDownloadUrl(artifact.id)}>
                          <Download size={14} />
                          Obter link
                        </button>
                        <button type="button" className="apoema-ghost-button" disabled={busyId === artifact.id} onClick={() => void handleDelete(artifact.id)}>
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

      {downloadUrl && (
        <section className="apoema-panel apoema-secure-link-panel">
          <div>
            <StatusPill tone="warning">URL assinada</StatusPill>
            <h2>Link temporário pronto</h2>
            <p>Expira em {formatDate(downloadUrl.expiresAt)}. O valor completo não é exibido para evitar vazamento visual.</p>
          </div>
          <button type="button" className="apoema-primary-button" onClick={() => void copyCurrentUrl()}>
            <Copy size={16} />
            Copiar URL assinada
          </button>
        </section>
      )}
    </div>
  );
}
