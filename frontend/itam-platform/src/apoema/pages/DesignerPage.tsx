import { useEffect, useMemo, useState } from "react";
import { Ban, Palette, RefreshCcw, RotateCcw, ShieldAlert, WandSparkles } from "lucide-react";
import { StatusPill } from "../components/StatusPill";
import {
  adjustDesignerJobItem,
  cancelDesignerJob,
  createDesignerBannerJob,
  getDesignerFormOptions,
  getDesignerHealth,
  listDesignerTemplates,
  refreshDesignerJobItemUrl,
} from "../lib/apoemaDesignerApi";
import { ApoemaApiError } from "../types";
import { useAuth } from "@/lib/auth";
import type { ApoemaDesignerFormOptions, ApoemaDesignerHealth, ApoemaDesignerJob, ApoemaDesignerTemplate } from "../lib/apoemaDesignerApi";

type PageState = "loading" | "ready" | "empty" | "unauthorized" | "unavailable" | "error";

type Banner = {
  title: string;
  message: string;
  tone: "warning" | "danger" | "success";
};

function describeError(error: unknown, resource: string): Banner {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required") return { tone: "danger", title: "Sessão necessária", message: `Faça login novamente para acessar ${resource}.` };
    if (error.kind === "forbidden") return { tone: "danger", title: "Sem permissão", message: `Seu perfil não pode executar esta ação mock.` };
    if (error.kind === "network_unavailable") return { tone: "warning", title: "Backend indisponível", message: `Não foi possível alcançar ${resource} em /api/v1.` };
    return { tone: "danger", title: "Erro da API", message: error.message };
  }
  return { tone: "danger", title: "Erro inesperado", message: `Falha ao consultar ${resource}.` };
}

function stateFromError(error: unknown): PageState {
  if (error instanceof ApoemaApiError) {
    if (error.kind === "auth_required" || error.kind === "forbidden") return "unauthorized";
    if (error.kind === "network_unavailable") return "unavailable";
  }
  return "error";
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "data indisponível";
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

export function DesignerPage() {
  const { token } = useAuth();
  const [health, setHealth] = useState<ApoemaDesignerHealth | null>(null);
  const [templates, setTemplates] = useState<ApoemaDesignerTemplate[]>([]);
  const [options, setOptions] = useState<ApoemaDesignerFormOptions | null>(null);
  const [job, setJob] = useState<ApoemaDesignerJob | null>(null);
  const [state, setState] = useState<PageState>("loading");
  const [jobState, setJobState] = useState<PageState>("empty");
  const [banner, setBanner] = useState<Banner | null>(null);
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({
    template_id: "",
    canal: "",
    kv: "",
    modo_geracao: "peca_unica",
    prompt: "Banner institucional determinístico para validação Apoema M6B.",
    copy: "Texto mock controlado pelo backend.",
    item_count: 1,
  });

  const selectedTemplate = useMemo(() => templates.find((template) => template.template_id === form.template_id) ?? null, [templates, form.template_id]);

  function seedForm(nextTemplates: ApoemaDesignerTemplate[], nextOptions: ApoemaDesignerFormOptions) {
    const first = nextTemplates[0];
    setForm((current) => ({
      ...current,
      template_id: current.template_id || first?.template_id || nextOptions.template_ids[0] || "",
      canal: current.canal || first?.canal || nextOptions.channels[0] || "",
      kv: current.kv || first?.kv || nextOptions.kvs[0] || "",
      modo_geracao: current.modo_geracao || first?.mode_options[0] || nextOptions.modes[0] || "peca_unica",
    }));
  }

  async function reload(guard: () => boolean = () => true) {
    setState("loading");
    setBanner(null);
    try {
      const [healthResult, templateResult, optionsResult] = await Promise.all([
        getDesignerHealth(token),
        listDesignerTemplates(token),
        getDesignerFormOptions(token),
      ]);
      if (!guard()) return;
      setHealth(healthResult);
      setTemplates(templateResult.items);
      setOptions(optionsResult);
      seedForm(templateResult.items, optionsResult);
      setState(templateResult.items.length > 0 ? "ready" : "empty");
    } catch (error) {
      if (!guard()) return;
      setHealth(null);
      setTemplates([]);
      setOptions(null);
      setState(stateFromError(error));
      setBanner(describeError(error, "Designer mock"));
    }
  }

  useEffect(() => {
    let active = true;
    void reload(() => active);
    return () => {
      active = false;
    };
  }, [token]);

  async function createJob() {
    setBusy(true);
    setJobState("loading");
    setBanner(null);
    try {
      const result = await createDesignerBannerJob(form, token);
      setJob(result);
      setJobState("ready");
      setBanner({ tone: "success", title: "Job mock criado", message: "Job determinístico criado no backend sem geração real de imagem." });
    } catch (error) {
      setJob(null);
      setJobState(stateFromError(error));
      setBanner(describeError(error, "criação de job Designer"));
    } finally {
      setBusy(false);
    }
  }

  async function runItemAction(action: "adjust" | "refresh", itemId: string) {
    if (!job) return;
    setBusy(true);
    setBanner(null);
    try {
      const result = action === "adjust" ? await adjustDesignerJobItem(job.job_id, itemId, token) : await refreshDesignerJobItemUrl(job.job_id, itemId, token);
      setJob(result);
      setJobState("ready");
      setBanner({ tone: "success", title: action === "adjust" ? "Item ajustado" : "Refresh solicitado", message: "Ação mock executada no backend; download-url segue bloqueado/não disponível nesta fase." });
    } catch (error) {
      setBanner(describeError(error, "ação de item Designer"));
    } finally {
      setBusy(false);
    }
  }

  async function cancelJob() {
    if (!job) return;
    setBusy(true);
    setBanner(null);
    try {
      await cancelDesignerJob(job.job_id, token);
      setJob({ ...job, status: "cancelled" });
      setBanner({ tone: "success", title: "Job cancelado", message: "Cancelamento mock registrado no backend." });
    } catch (error) {
      setBanner(describeError(error, "cancelamento Designer"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="apoema-page apoema-stub-page">
      <section className="apoema-page-top">
        <div>
          <StatusPill tone="warning">Mock determinístico</StatusPill>
          <h1>Designer Mock</h1>
          <p>Jobs determinísticos backend-owned para banners JSON. Não há geração real de imagem nem provider real nesta fase.</p>
        </div>
        <button type="button" className="apoema-secondary-button" onClick={() => void reload()}>
          <RotateCcw size={16} />
          Recarregar
        </button>
      </section>

      <div className="apoema-warning is-warning">
        <ShieldAlert size={16} />
        <div>
          <strong>Sem provider real e sem imagem real</strong>
          <p>A UI chama somente /api/v1/designer. Download-url bloqueado/não disponível fica explícito e nenhuma chave de provider é criada no frontend.</p>
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

      <section className="apoema-stub-grid">
        <article className="apoema-panel">
          <div className="apoema-section-head">
            <div>
              <StatusPill tone="info">Health</StatusPill>
              <h2>Estado do adapter</h2>
            </div>
            <span>{state}</span>
          </div>
          {state === "loading" && <div className="apoema-empty-state">Carregando Designer API...</div>}
          {state === "empty" && <div className="apoema-empty-state"><strong>Sem templates</strong><p>Backend retornou catálogo vazio.</p></div>}
          {state === "unauthorized" && <div className="apoema-empty-state"><strong>Sessão/permissão necessária</strong><p>Chamada recusada pelo backend.</p></div>}
          {state === "unavailable" && <div className="apoema-empty-state"><strong>Backend indisponível</strong><p>Sem fallback falso ou provider direto.</p></div>}
          {state === "error" && <div className="apoema-empty-state"><strong>Erro operacional</strong><p>Falha ao carregar Designer API.</p></div>}
          {health && (
            <dl className="apoema-detail-grid">
              <div><dt>Modo</dt><dd>{health.mode}</dd></div>
              <div><dt>Determinístico</dt><dd>{health.deterministic ? "sim" : "não"}</dd></div>
              <div><dt>Provider real</dt><dd>{health.provider_real_enabled ? "ativo" : "desativado"}</dd></div>
              <div><dt>Templates</dt><dd>{health.template_count}</dd></div>
            </dl>
          )}
        </article>

        <article className="apoema-panel">
          <StatusPill tone="warning">Formulário controlado</StatusPill>
          <div className="apoema-form-stack">
            <label className="apoema-field">Template
              <select value={form.template_id} onChange={(event) => setForm((current) => ({ ...current, template_id: event.target.value }))}>
                {templates.map((template) => <option key={template.template_id} value={template.template_id}>{template.label}</option>)}
              </select>
            </label>
            <label className="apoema-field">Canal
              <select value={form.canal} onChange={(event) => setForm((current) => ({ ...current, canal: event.target.value }))}>
                {(options?.channels ?? []).map((channel) => <option key={channel} value={channel}>{channel}</option>)}
              </select>
            </label>
            <label className="apoema-field">KV
              <select value={form.kv} onChange={(event) => setForm((current) => ({ ...current, kv: event.target.value }))}>
                {(options?.kvs ?? []).map((kv) => <option key={kv} value={kv}>{kv}</option>)}
              </select>
            </label>
            <label className="apoema-field">Modo de geração
              <select value={form.modo_geracao} onChange={(event) => setForm((current) => ({ ...current, modo_geracao: event.target.value }))}>
                {(selectedTemplate?.mode_options ?? options?.modes ?? []).map((mode) => <option key={mode} value={mode}>{mode}</option>)}
              </select>
            </label>
            <label className="apoema-field">Prompt
              <textarea value={form.prompt} onChange={(event) => setForm((current) => ({ ...current, prompt: event.target.value }))} />
            </label>
            <button type="button" className="apoema-primary-button" disabled={busy || !form.template_id} onClick={() => void createJob()}>
              <WandSparkles size={16} />
              Criar job mock
            </button>
          </div>
        </article>
      </section>

      <section className="apoema-panel">
        <div className="apoema-section-head">
          <div>
            <StatusPill tone="info">Job</StatusPill>
            <h2>Resultado determinístico</h2>
          </div>
          <span>{jobState}</span>
        </div>
        {jobState === "loading" && <div className="apoema-empty-state">Criando job no backend...</div>}
        {jobState === "empty" && <div className="apoema-empty-state"><strong>Nenhum job criado</strong><p>Preencha o formulário para validar o adapter Designer mock.</p></div>}
        {(jobState === "unauthorized" || jobState === "unavailable" || jobState === "error") && <div className="apoema-empty-state"><strong>Job indisponível</strong><p>O backend não retornou job válido.</p></div>}
        {job && (
          <div className="apoema-card-list">
            <article className="apoema-stub-card">
              <div className="apoema-card-headline">
                <Palette size={16} />
                <strong>Job {job.job_id}</strong>
                <StatusPill tone="warning">{job.status}</StatusPill>
              </div>
              <p>{job.summary}</p>
              <small>{job.template_id} · {job.kv} · {formatDate(job.created_at)}</small>
              <div className="apoema-row-actions">
                <button type="button" className="apoema-ghost-button" disabled={busy} onClick={() => void cancelJob()}><Ban size={14} />Cancelar</button>
              </div>
            </article>
            {job.items.map((item) => (
              <article key={item.item_id} className="apoema-stub-card">
                <strong>{item.title}</strong>
                <p>{item.result_note}</p>
                <small>Download-url bloqueado/não disponível · status {item.status}</small>
                <div className="apoema-row-actions">
                  <button type="button" className="apoema-secondary-button" disabled={busy} onClick={() => void runItemAction("adjust", item.item_id)}><WandSparkles size={14} />Ajustar mock</button>
                  <button type="button" className="apoema-secondary-button" disabled={busy} onClick={() => void runItemAction("refresh", item.item_id)}><RefreshCcw size={14} />Refresh mock</button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
