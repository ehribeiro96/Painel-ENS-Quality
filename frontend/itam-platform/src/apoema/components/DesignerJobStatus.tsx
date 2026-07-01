import { Ban, RefreshCcw, ShieldAlert } from "lucide-react";
import { StatusPill } from "./StatusPill";
import type { DesignerHealth, DesignerJob } from "../types";

function statusTone(status: DesignerJob["status"]) {
  switch (status) {
    case "completed":
      return "success";
    case "running":
      return "info";
    case "queued":
      return "neutral";
    case "cancelled":
    case "failed":
    case "expired":
      return "warning";
    default:
      return "neutral";
  }
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "data indisponível";
  }
  return date.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

type Props = {
  job: DesignerJob;
  health?: DesignerHealth | null;
  busy?: boolean;
  onReload: () => void | Promise<void>;
  onCancel: () => void | Promise<void>;
};

export function DesignerJobStatus({ job, health = null, busy = false, onReload, onCancel }: Props) {
  return (
    <section className="apoema-designer-job-status">
      <div className="apoema-section-head">
        <div>
          <StatusPill tone={statusTone(job.status)}>{job.status}</StatusPill>
          <h2>Job {job.job_id}</h2>
          <p>{job.summary}</p>
        </div>
        <div className="apoema-designer-job-status-actions">
          <button type="button" className="apoema-secondary-button" onClick={() => void onReload()} disabled={busy}>
            <RefreshCcw size={16} />
            Recarregar
          </button>
          <button type="button" className="apoema-ghost-button" onClick={() => void onCancel()} disabled={busy || job.status === "cancelled"}>
            <Ban size={16} />
            Cancelar job
          </button>
        </div>
      </div>

      <div className="apoema-designer-job-status-note">
        <ShieldAlert size={16} />
        <div>
          <strong>Mock determinístico</strong>
          <p>Provider real e download-url permanecem indisponíveis. A interface apenas lê e manipula o job backend-owned.</p>
        </div>
      </div>

      <dl className="apoema-designer-job-meta">
        <div>
          <dt>Template</dt>
          <dd>{job.template_id}</dd>
        </div>
        <div>
          <dt>Canal</dt>
          <dd>{job.canal}</dd>
        </div>
        <div>
          <dt>KV</dt>
          <dd>{job.kv}</dd>
        </div>
        <div>
          <dt>Modo</dt>
          <dd>{job.modo_geracao}</dd>
        </div>
        <div>
          <dt>Progresso</dt>
          <dd>{Math.round(job.progress)}%</dd>
        </div>
        <div>
          <dt>Itens</dt>
          <dd>{job.items.length}</dd>
        </div>
        <div>
          <dt>Criado em</dt>
          <dd>{formatDate(job.created_at)}</dd>
        </div>
        <div>
          <dt>Atualizado em</dt>
          <dd>{formatDate(job.updated_at)}</dd>
        </div>
        <div>
          <dt>Provider real</dt>
          <dd>{health?.provider_real_enabled ? "ativo" : "desativado"}</dd>
        </div>
        <div>
          <dt>Determinístico</dt>
          <dd>{health?.deterministic ? "sim" : "não"}</dd>
        </div>
      </dl>

      <div className="apoema-designer-progress" aria-label="Progresso do job">
        <div className="apoema-designer-progress-bar">
          <span style={{ width: `${Math.max(0, Math.min(100, job.progress))}%` }} />
        </div>
        <small>{job.persona_image_present ? "persona_image presente" : "sem persona_image"} · {job.box2 ? "box2 informado" : "sem box2"} · sem output de storage</small>
      </div>
    </section>
  );
}
