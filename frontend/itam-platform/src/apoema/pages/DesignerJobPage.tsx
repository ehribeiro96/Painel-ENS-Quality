import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, RefreshCcw, ShieldAlert } from "lucide-react";
import { DesignerJobItems } from "../components/DesignerJobItems";
import { DesignerJobStatus } from "../components/DesignerJobStatus";
import { StatusPill } from "../components/StatusPill";
import {
  adjustDesignerJobItem,
  cancelDesignerJob,
  getDesignerHealth,
  getDesignerJob,
  refreshDesignerJobItemUrl,
} from "../lib/apoemaDesignerApi";
import { ApoemaApiError } from "../types";
import { useAuth } from "@/lib/auth";
import type { DesignerHealth, DesignerJob, DesignerJobItem } from "../types";

type DetailState = "loading" | "ready" | "unauthorized" | "forbidden" | "not_found" | "conflict" | "expired" | "validation" | "rate_limited" | "unavailable" | "error";

type BannerTone = "warning" | "danger" | "success";

type Banner = {
  tone: BannerTone;
  title: string;
  message: string;
};

function describeError(error: unknown, resource: string): Banner {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return { tone: "danger", title: "Sua sessão expirou ou não foi autenticada.", message: `Faça login novamente para acessar ${resource}.` };
    if (error.kind === "forbidden") return { tone: "danger", title: "Você não tem permissão para usar o Designer.", message: `Seu perfil não pode acessar ${resource}.` };
    if (error.kind === "not_found") return { tone: "warning", title: "Template, job ou item não encontrado.", message: `O backend não retornou ${resource}.` };
    if (error.kind === "conflict") return { tone: "warning", title: "O job está em um estado incompatível com esta ação.", message: `O backend rejeitou a operação em ${resource}.` };
    if (error.kind === "expired") return { tone: "warning", title: "Este recurso não está mais disponível.", message: `O backend informou que ${resource} expirou ou foi removido.` };
    if (error.kind === "validation_error") return { tone: "warning", title: "Revise os campos do formulário.", message: `O backend recusou os dados enviados para ${resource}.` };
    if (error.kind === "rate_limited") return { tone: "warning", title: "Limite de geração atingido. Tente novamente mais tarde.", message: `O backend limitou a operação em ${resource}.` };
    if (error.kind === "network_unavailable") return { tone: "warning", title: "Falha de rede ao acessar o Designer.", message: `Não foi possível alcançar ${resource} em /api/v1/designer.` };
    if (error.kind === "backend_error") return { tone: "danger", title: "Backend Designer indisponível.", message: error.message };
    return { tone: "danger", title: "Erro da API", message: error.message };
  }
  return { tone: "danger", title: "Erro inesperado", message: `Falha ao consultar ${resource}.` };
}

function stateFromError(error: unknown): DetailState {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return "unauthorized";
    if (error.kind === "forbidden") return "forbidden";
    if (error.kind === "not_found") return "not_found";
    if (error.kind === "conflict") return "conflict";
    if (error.kind === "expired") return "expired";
    if (error.kind === "validation_error") return "validation";
    if (error.kind === "rate_limited") return "rate_limited";
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

function jobReference(jobId: string) {
  return `Job ${jobId}`;
}

export function DesignerJobPage() {
  const { jobId } = useParams();
  const { token } = useAuth();
  const [job, setJob] = useState<DesignerJob | null>(null);
  const [health, setHealth] = useState<DesignerHealth | null>(null);
  const [state, setState] = useState<DetailState>("loading");
  const [banner, setBanner] = useState<Banner | null>(null);
  const [busy, setBusy] = useState(false);
  const [busyItemId, setBusyItemId] = useState<string | null>(null);

  async function reload(guard: () => boolean = () => true) {
    if (!jobId) {
      setJob(null);
      setState("not_found");
      return;
    }
    setState("loading");
    setBanner(null);
    try {
      const [jobResult, healthResult] = await Promise.all([getDesignerJob(jobId, token), getDesignerHealth(token)]);
      if (!guard()) return;
      setJob(jobResult);
      setHealth(healthResult);
      setState("ready");
    } catch (error) {
      if (!guard()) return;
      setJob(null);
      setHealth(null);
      setState(stateFromError(error));
      setBanner(describeError(error, jobReference(jobId)));
    }
  }

  useEffect(() => {
    let active = true;
    void reload(() => active);
    return () => {
      active = false;
    };
  }, [jobId, token]);

  async function handleAdjust(item: DesignerJobItem) {
    if (!job) return;
    const adjustmentPrompt = window.prompt(`Informe o ajuste para o item ${item.item_id}:`, "");
    if (!adjustmentPrompt?.trim()) {
      return;
    }
    setBusy(true);
    setBusyItemId(item.item_id);
    setBanner(null);
    try {
      const result = await adjustDesignerJobItem(job.job_id, item.item_id, { adjustment_prompt: adjustmentPrompt.trim() }, token);
      setJob(result);
      setState("ready");
      setBanner({ tone: "success", title: "Item ajustado", message: "Ajuste determinístico registrado pelo backend." });
    } catch (error) {
      setBanner(describeError(error, "ajuste do item"));
    } finally {
      setBusy(false);
      setBusyItemId(null);
    }
  }

  async function handleRefresh(item: DesignerJobItem) {
    if (!job) return;
    const reason = window.prompt(`Motivo do refresh-url para o item ${item.item_id}:`, "");
    if (!reason?.trim()) {
      return;
    }
    setBusy(true);
    setBusyItemId(item.item_id);
    setBanner(null);
    try {
      const result = await refreshDesignerJobItemUrl(job.job_id, item.item_id, { reason: reason.trim() }, token);
      setJob(result);
      setState("ready");
      setBanner({ tone: "success", title: "Refresh solicitado", message: "O backend registrou o refresh-url determinístico." });
    } catch (error) {
      setBanner(describeError(error, "refresh-url do item"));
    } finally {
      setBusy(false);
      setBusyItemId(null);
    }
  }

  async function handleCancel() {
    if (!job) return;
    const confirmed = window.confirm(`Cancelar o job ${job.job_id}? Esta ação é irreversível e será registrada pelo backend.`);
    if (!confirmed) {
      return;
    }
    setBusy(true);
    setBanner(null);
    try {
      await cancelDesignerJob(job.job_id, token);
      await reload();
      setBanner({ tone: "success", title: "Job cancelado", message: "Cancelamento mock registrado no backend." });
    } catch (error) {
      setBanner(describeError(error, "cancelamento do job"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="apoema-page apoema-designer-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="info">Job Designer</StatusPill>
          <h1>Detalhe do job</h1>
          <p>Job backend-owned, sem download-url real, sem provider real e sem renderização de path interno.</p>
        </div>
        <div className="apoema-rag-page-actions">
          <Link className="apoema-secondary-button" to="..">
            <ArrowLeft size={16} />
            Voltar
          </Link>
          <button type="button" className="apoema-secondary-button" onClick={() => void reload()} disabled={state === "loading" || busy}>
            <RefreshCcw size={16} />
            Recarregar
          </button>
        </div>
      </section>

      <div className="apoema-warning is-warning">
        <ShieldAlert size={16} />
        <div>
          <strong>Contrato honesto</strong>
          <p>Adjust e refresh-url são os únicos atos expostos. Download-url continua indisponível nesta fase.</p>
        </div>
      </div>

      {banner ? (
        <div className={`apoema-warning ${banner.tone === "danger" ? "is-danger" : "is-warning"}`}>
          <ShieldAlert size={16} />
          <div>
            <strong>{banner.title}</strong>
            <p>{banner.message}</p>
          </div>
        </div>
      ) : null}

      <section className="apoema-designer-grid">
        <article className="apoema-panel">
          <div className="apoema-section-head">
            <div>
              <StatusPill tone="info">Status</StatusPill>
              <h2>{job ? jobReference(job.job_id) : "Carregando..."}</h2>
              <p>O backend retorna o job completo e controla os estados de item.</p>
            </div>
            <span>{state}</span>
          </div>

          {state === "loading" ? <div className="apoema-empty-state">Carregando job...</div> : null}
          {state === "unauthorized" ? (
            <div className="apoema-empty-state">
              <strong>Sessão necessária</strong>
              <p>Faça login novamente para acessar o job.</p>
            </div>
          ) : null}
          {state === "forbidden" ? (
            <div className="apoema-empty-state">
              <strong>Sem permissão</strong>
              <p>Seu perfil não pode acessar este job.</p>
            </div>
          ) : null}
          {state === "not_found" ? (
            <div className="apoema-empty-state">
              <strong>Job não encontrado</strong>
              <p>O backend não retornou este job.</p>
            </div>
          ) : null}
          {state === "conflict" ? (
            <div className="apoema-empty-state">
              <strong>Estado incompatível</strong>
              <p>O backend rejeitou a ação por conflito de estado.</p>
            </div>
          ) : null}
          {state === "expired" ? (
            <div className="apoema-empty-state">
              <strong>Recurso expirado</strong>
              <p>O job não está mais disponível.</p>
            </div>
          ) : null}
          {state === "validation" ? (
            <div className="apoema-empty-state">
              <strong>Validação pendente</strong>
              <p>Revise os campos enviados ao backend.</p>
            </div>
          ) : null}
          {state === "rate_limited" ? (
            <div className="apoema-empty-state">
              <strong>Limite atingido</strong>
              <p>Espere alguns instantes e tente novamente.</p>
            </div>
          ) : null}
          {state === "unavailable" ? (
            <div className="apoema-empty-state">
              <strong>Backend indisponível</strong>
              <p>Falha de rede ao acessar /api/v1/designer.</p>
            </div>
          ) : null}
          {state === "error" ? (
            <div className="apoema-empty-state">
              <strong>Erro operacional</strong>
              <p>Falha ao carregar o detalhe do job.</p>
            </div>
          ) : null}

          {job ? <DesignerJobStatus job={job} health={health} busy={busy} onReload={() => void reload()} onCancel={() => void handleCancel()} /> : null}

          {job ? (
            <div className="apoema-designer-job-foot">
              <small>Criado em {formatDate(job.created_at)}</small>
              <small>Atualizado em {formatDate(job.updated_at)}</small>
              <small>O backend não expõe download-url nesta fase.</small>
            </div>
          ) : null}
        </article>

        {job ? (
          <DesignerJobItems items={job.items} busyItemId={busyItemId} onAdjust={(item) => void handleAdjust(item)} onRefreshUrl={(item) => void handleRefresh(item)} />
        ) : (
          <section className="apoema-panel">
            <div className="apoema-section-head">
              <div>
                <StatusPill tone="neutral">Itens</StatusPill>
                <h2>Nenhum conteúdo carregado</h2>
              </div>
            </div>
            <div className="apoema-empty-state">
              <strong>Sem job</strong>
              <p>Abra um job existente ou crie um novo em /apoema/designer.</p>
            </div>
          </section>
        )}
      </section>
    </div>
  );
}
