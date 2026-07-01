import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { RefreshCcw, ShieldAlert, Sparkles } from "lucide-react";
import { DesignerBannerForm } from "../components/DesignerBannerForm";
import { DesignerJobStatus } from "../components/DesignerJobStatus";
import { StatusPill } from "../components/StatusPill";
import {
  cancelDesignerJob,
  createDesignerBannerJson,
  getDesignerFormOptions,
  getDesignerHealth,
  getDesignerJob,
  getDesignerTemplates,
} from "../lib/apoemaDesignerApi";
import { ApoemaApiError } from "../types";
import { useAuth } from "@/lib/auth";
import type { DesignerBannerJsonRequest, DesignerFormOptions, DesignerHealth, DesignerJob, DesignerTemplate } from "../types";

type PageState = "loading" | "ready" | "empty" | "unauthorized" | "forbidden" | "conflict" | "expired" | "validation" | "rate_limited" | "unavailable" | "error";

type BannerTone = "warning" | "danger" | "success";

type Banner = {
  title: string;
  message: string;
  tone: BannerTone;
};

type DesignerBannerDraft = Pick<DesignerBannerJsonRequest, "template_id" | "modo_geracao" | "prompt" | "copy" | "box2" | "item_count"> & {
  canal: string;
  kv: string;
};

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "data indisponível";
  }
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

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

function stateFromError(error: unknown): PageState {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return "unauthorized";
    if (error.kind === "forbidden") return "forbidden";
    if (error.kind === "conflict") return "conflict";
    if (error.kind === "expired") return "expired";
    if (error.kind === "validation_error") return "validation";
    if (error.kind === "rate_limited") return "rate_limited";
    if (error.kind === "network_unavailable") return "unavailable";
  }
  return "error";
}

function defaultDraft(nextTemplates: DesignerTemplate[], nextOptions: DesignerFormOptions): DesignerBannerDraft {
  const firstTemplate = nextTemplates[0];
  const firstMode = firstTemplate?.mode_options[0] ?? nextOptions.modes[0] ?? "peca_unica";
  return {
    template_id: firstTemplate?.template_id ?? nextOptions.template_ids[0] ?? "",
    canal: firstTemplate?.canal ?? nextOptions.channels[0] ?? "",
    kv: firstTemplate?.kv ?? nextOptions.kvs[0] ?? "",
    modo_geracao: firstMode,
    prompt: "Banner institucional determinístico para validação Apoema M10B.",
    copy: "Texto mock controlado pelo backend.",
    box2: "",
    item_count: 1,
  };
}

export function DesignerPage() {
  const { token } = useAuth();
  const [health, setHealth] = useState<DesignerHealth | null>(null);
  const [templates, setTemplates] = useState<DesignerTemplate[]>([]);
  const [options, setOptions] = useState<DesignerFormOptions | null>(null);
  const [draft, setDraft] = useState<DesignerBannerDraft>({
    template_id: "",
    canal: "",
    kv: "",
    modo_geracao: "peca_unica",
    prompt: "Banner institucional determinístico para validação Apoema M10B.",
    copy: "Texto mock controlado pelo backend.",
    box2: "",
    item_count: 1,
  });
  const [job, setJob] = useState<DesignerJob | null>(null);
  const [state, setState] = useState<PageState>("loading");
  const [jobState, setJobState] = useState<PageState>("empty");
  const [banner, setBanner] = useState<Banner | null>(null);
  const [busy, setBusy] = useState(false);

  async function reload(guard: () => boolean = () => true) {
    setState("loading");
    setBanner(null);
    try {
      const [healthResult, templateResult, optionsResult] = await Promise.all([
        getDesignerHealth(token),
        getDesignerTemplates(token),
        getDesignerFormOptions(token),
      ]);
      if (!guard()) return;
      setHealth(healthResult);
      setTemplates(templateResult.items);
      setOptions(optionsResult);
      setDraft(defaultDraft(templateResult.items, optionsResult));
      setState(templateResult.items.length > 0 ? "ready" : "empty");
    } catch (error) {
      if (!guard()) return;
      setHealth(null);
      setTemplates([]);
      setOptions(null);
      setDraft((current) => ({ ...current, template_id: "", canal: "", kv: "" }));
      setState(stateFromError(error));
      setBanner(describeError(error, "catálogo Designer"));
    }
  }

  useEffect(() => {
    let active = true;
    void reload(() => active);
    return () => {
      active = false;
    };
  }, [token]);

  async function reloadJob(nextJobId: string, guard: () => boolean = () => true) {
    try {
      const result = await getDesignerJob(nextJobId, token);
      if (!guard()) return;
      setJob(result);
      setJobState("ready");
    } catch (error) {
      if (!guard()) return;
      setJob(null);
      setJobState(stateFromError(error));
      setBanner(describeError(error, "detalhe do job"));
    }
  }

  async function createJob() {
    setBusy(true);
    setJobState("loading");
    setBanner(null);
    try {
      const result = await createDesignerBannerJson(draft as DesignerBannerJsonRequest, token);
      setJob(result);
      setJobState("ready");
      setBanner({ tone: "success", title: "Job mock criado", message: "Job determinístico criado no backend sem provider real e sem download-url." });
      setState((current) => (current === "empty" ? "ready" : current));
    } catch (error) {
      setJob(null);
      setJobState(stateFromError(error));
      setBanner(describeError(error, "criação de job Designer"));
    } finally {
      setBusy(false);
    }
  }

  async function cancelCurrentJob() {
    if (!job) return;
    const confirmed = window.confirm(`Cancelar o job ${job.job_id}? Esta ação é irreversível e será registrada pelo backend.`);
    if (!confirmed) return;
    setBusy(true);
    setBanner(null);
    try {
      await cancelDesignerJob(job.job_id, token);
      await reloadJob(job.job_id);
      setBanner({ tone: "success", title: "Job cancelado", message: "Cancelamento mock registrado no backend." });
    } catch (error) {
      setBanner(describeError(error, "cancelamento Designer"));
    } finally {
      setBusy(false);
    }
  }

  async function reloadCurrentJob() {
    if (!job) return;
    setBusy(true);
    setBanner(null);
    try {
      await reloadJob(job.job_id);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="apoema-page apoema-designer-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone={health?.provider_real_enabled ? "success" : "warning"}>
            <Sparkles size={14} />
            {health?.provider_real_enabled ? "Provider real" : "Designer Mock"}
          </StatusPill>
          <h1>Designer</h1>
          <p>Mock determinístico via backend Designer. Provider real e download-url não estão disponíveis nesta fase.</p>
        </div>
        <button type="button" className="apoema-secondary-button" onClick={() => void reload()} disabled={state === "loading" || busy}>
          <RefreshCcw size={16} />
          Recarregar
        </button>
      </section>

      <div className="apoema-warning is-warning">
        <ShieldAlert size={16} />
        <div>
          <strong>Contrato honesto</strong>
          <p>
            Não há geração real de imagem nem provider real. Sem geração real de imagem e nenhuma chave de provider no frontend. Download-url bloqueado/não disponível nesta fase.
            A UI chama somente /api/v1/designer, sem upload de imagem e sem integração com Artifact, Chat ou RAG.
          </p>
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
              <StatusPill tone="info">Health</StatusPill>
              <h2>Estado do adapter</h2>
            </div>
            <span>{state}</span>
          </div>

          {state === "loading" ? <div className="apoema-empty-state">Carregando Designer API...</div> : null}
          {state === "empty" ? (
            <div className="apoema-empty-state">
              <strong>Sem templates</strong>
              <p>O backend não retornou catálogo disponível.</p>
            </div>
          ) : null}
          {state === "unauthorized" ? (
            <div className="apoema-empty-state">
              <strong>Sessão necessária</strong>
              <p>Faça login novamente para acessar o Designer.</p>
            </div>
          ) : null}
          {state === "forbidden" ? (
            <div className="apoema-empty-state">
              <strong>Sem permissão</strong>
              <p>Seu perfil não pode acessar o Designer.</p>
            </div>
          ) : null}
          {state === "conflict" ? (
            <div className="apoema-empty-state">
              <strong>Estado incompatível</strong>
              <p>O backend rejeitou a operação por conflito de estado.</p>
            </div>
          ) : null}
          {state === "expired" ? (
            <div className="apoema-empty-state">
              <strong>Recurso indisponível</strong>
              <p>O recurso não está mais disponível.</p>
            </div>
          ) : null}
          {state === "validation" ? (
            <div className="apoema-empty-state">
              <strong>Validação pendente</strong>
              <p>Revise os dados retornados pelo backend.</p>
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
              <p>Falha ao carregar o Designer.</p>
            </div>
          ) : null}

          {health ? (
            <>
              <dl className="apoema-detail-grid">
                <div>
                  <dt>Modo</dt>
                  <dd>{health.mode}</dd>
                </div>
                <div>
                  <dt>Determinístico</dt>
                  <dd>{health.deterministic ? "sim" : "não"}</dd>
                </div>
                <div>
                  <dt>Provider real</dt>
                  <dd>{health.provider_real_enabled ? "ativo" : "desativado"}</dd>
                </div>
                <div>
                  <dt>Templates</dt>
                  <dd>{health.template_count}</dd>
                </div>
                <div>
                  <dt>Jobs</dt>
                  <dd>{health.job_count}</dd>
                </div>
                <div>
                  <dt>Status</dt>
                  <dd>{health.status}</dd>
                </div>
              </dl>
              <div className="apoema-designer-health-note">{health.note}</div>
            </>
          ) : null}
        </article>

        <DesignerBannerForm
          templates={templates}
          formOptions={options}
          value={draft}
          onChange={setDraft}
          onSubmit={() => void createJob()}
          disabled={busy || templates.length === 0 || !options}
          loading={busy}
          catalogLoading={state === "loading"}
          banner={jobState === "loading" ? "Criando job no backend..." : null}
        />
      </section>

      {job ? (
        <section className="apoema-panel">
          <div className="apoema-section-head">
            <div>
              <StatusPill tone="success">Job criado</StatusPill>
              <h2>Resumo do job</h2>
            </div>
            <Link className="apoema-secondary-button" to={`jobs/${job.job_id}`}>
              Ver detalhe
            </Link>
          </div>

          <DesignerJobStatus job={job} health={health} busy={busy} onReload={() => void reloadCurrentJob()} onCancel={() => void cancelCurrentJob()} />

          <div className="apoema-designer-created-job-foot">
            <small>Job backend-owned criado em {formatDate(job.created_at)}.</small>
            <small>O detalhe completo fica disponível em /apoema/designer/jobs/{job.job_id}.</small>
          </div>
        </section>
      ) : (
        <section className="apoema-panel">
          <div className="apoema-section-head">
            <div>
              <StatusPill tone="info">Criação</StatusPill>
              <h2>Nenhum job criado</h2>
            </div>
            <span>{jobState}</span>
          </div>
          {jobState === "loading" ? (
            <div className="apoema-empty-state">Criando job no backend...</div>
          ) : (
            <div className="apoema-empty-state">
              <strong>Pronto para criar</strong>
              <p>Selecione um template, ajuste o briefing e crie um job deterministicamente controlado pelo backend.</p>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
