import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { FileUp, Upload } from "lucide-react";

import { DataTable } from "@/components/DataTable";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44ImportPanel } from "@/components/base44/Base44ImportPanel";
import { Base44InfoGrid } from "@/components/base44/Base44InfoGrid";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDateTime, formatImportDecision, formatTechnicalLabel } from "@/lib/format";
import type { ImportConflict, ImportJob, ImportPreview, ImportStagingAsset, ImportValidationError, Page } from "@/lib/types";

const FIELD_OPTIONS = [
  "hostname",
  "serial",
  "patrimony",
  "manufacturer",
  "model",
  "asset_type",
  "fallback_asset_type",
  "user",
  "user_email",
  "location",
  "operating_system",
  "ip_address",
  "last_login",
  "status",
  "notes",
  "source_state",
  "source_metadata.unit",
  "source_metadata.network_location",
  "source_metadata.imported_user_hint",
  "source_metadata.first_seen",
  "source_metadata.last_tried",
  "source_metadata.fqdn",
  "source_metadata.dns_name",
  "source_metadata.source_notes",
  "source_metadata.source"
];

const IMPORT_MODES = ["INITIAL_LOAD", "SAFE_REIMPORT", "PREVIEW_ONLY"];

function issueText(issue: Record<string, unknown>) {
  return String(issue.message ?? issue.suggested_action ?? issue.code ?? "Sem detalhe.");
}

function conflictText(conflict: ImportConflict) {
  const details = conflict.details ?? {};
  const identity = [details.identity_type, details.identity_value].filter(Boolean).join(" ");
  const rows = Array.isArray(details.rows) ? `Linhas ${details.rows.join(", ")}` : "";
  const suggested = details.suggested_action ? ` Ação sugerida: ${details.suggested_action}` : "";
  return `${details.message ?? conflict.conflict_type}${identity ? ` (${identity})` : ""}${rows ? ` - ${rows}` : ""}.${suggested}`;
}

export function ImportsPage() {
  const { token } = useAuth();
  const [page, setPage] = useState<Page<ImportJob> | null>(null);
  const [selected, setSelected] = useState<ImportJob | null>(null);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [staging, setStaging] = useState<Page<ImportStagingAsset> | null>(null);
  const [conflicts, setConflicts] = useState<ImportConflict[]>([]);
  const [validationErrors, setValidationErrors] = useState<ImportValidationError[]>([]);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [importMode, setImportMode] = useState("INITIAL_LOAD");
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function loadImports(nextSelectedId?: string) {
    if (!token) return;
    setLoading(true);
    api
      .imports(token)
      .then((data) => {
        setPage(data);
        const next = data.items.find((item) => item.id === nextSelectedId) ?? data.items[0] ?? null;
        setSelected(next);
        setError(null);
      })
      .catch(() => setError("Não foi possível carregar as importações."))
      .finally(() => setLoading(false));
  }

  function loadDetails(job: ImportJob | null) {
    if (!token || !job) {
      setPreview(null);
      setStaging(null);
      setConflicts([]);
      setValidationErrors([]);
      return;
    }
    Promise.all([
      api.importPreview(token, job.id),
      api.importStaging(token, job.id),
      api.importConflicts(token, job.id),
      api.importValidationErrors(token, job.id)
    ])
      .then(([previewData, stagingData, conflictData, errorData]) => {
        setPreview(previewData);
        setStaging(stagingData);
        setConflicts(conflictData);
        setValidationErrors(errorData);
        setMapping(previewData.detected_mapping ?? {});
        setImportMode(String(previewData.job.report.import_mode ?? "INITIAL_LOAD"));
      })
      .catch(() => setError("Não foi possível carregar preview, staging ou conflitos."));
  }

  useEffect(() => loadImports(), [token]);
  useEffect(() => loadDetails(selected), [selected?.id, token]);

  async function handleFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !token) return;
    setUploading(true);
    setMessage(null);
    setError(null);
    try {
      const job = await api.importUpload(token, file, importMode);
      setMessage("Arquivo enviado para staging. Revise preview, mapeamento e conflitos antes de aplicar.");
      loadImports(job.id);
    } catch {
      setError("Falha no upload. Verifique extensão CSV/XLSX, tamanho, fórmulas e permissões.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function saveMapping() {
    if (!token || !selected) return;
    try {
      const job = await api.updateImportMapping(token, selected.id, mapping, importMode);
      setSelected(job);
      setMessage("Mapeamento salvo para esta importação.");
    } catch {
      setError("Não foi possível salvar o mapeamento.");
    }
  }

  async function applyImport() {
    if (!token || !selected) return;
    const report = selected.report as Record<string, unknown>;
    if (report.can_apply === false || selected.conflict_rows > 0) {
      const blockers = Array.isArray(report.apply_blockers) ? report.apply_blockers.join(" ") : "Revise bloqueadores antes de aplicar.";
      setError(blockers);
      return;
    }
    if (selected.report.import_mode === "PREVIEW_ONLY") {
      setError("Esta importação está em modo PREVIEW_ONLY e não permite apply.");
      return;
    }
    if (!window.confirm("Aplicar importação? Dados operacionais críticos não serão sobrescritos automaticamente.")) return;
    setApplying(true);
    setError(null);
    try {
      const result = await api.applyImport(token, selected.id);
      setSelected(result.job);
      setMessage("Importação aplicada com relatório final e auditoria.");
      loadImports(result.job.id);
    } catch {
      setError("Falha ao aplicar importação.");
    } finally {
      setApplying(false);
    }
  }

  async function cancelImport() {
    if (!token || !selected) return;
    if (!window.confirm("Cancelar importação pendente? O staging será preservado para auditoria.")) return;
    try {
      const job = await api.cancelImport(token, selected.id);
      setSelected(job);
      setMessage("Importação cancelada.");
      loadImports(job.id);
    } catch {
      setError("Não foi possível cancelar a importação.");
    }
  }

  const latest = selected ?? page?.items[0];
  const report = (latest?.report ?? {}) as Record<string, unknown>;
  const warnings = Array.isArray(report.warnings) ? report.warnings.map(String) : [];
  const summary = (report.summary ?? {}) as Record<string, number>;
  const quality = (report.quality ?? {}) as Record<string, number>;
  const distributions = (report.distributions ?? {}) as Record<string, Record<string, number>>;
  const metrics = useMemo(
    () => [
      ["Total de linhas", latest?.total_rows ?? 0, ""],
      ["Prontas para aplicar", latest?.valid_rows ?? 0, "success"],
      ["Exigem revisão", (latest?.conflict_rows ?? 0) + (latest?.invalid_rows ?? 0), "warning"],
      ["Inválidas", latest?.invalid_rows ?? 0, latest?.invalid_rows ? "danger" : ""],
      ["Conflitos", latest?.conflict_rows ?? 0, latest?.conflict_rows ? "danger" : ""]
    ],
    [latest]
  );

  const canApply = selected && !["APPLIED", "APPLIED_WITH_ISSUES", "CANCELLED"].includes(selected.status);
  const reportCanApply = selected ? selected.report.can_apply !== false : false;
  const blockers = Array.isArray(report.apply_blockers) ? report.apply_blockers.map(String) : [];
  const hasConflicts = (latest?.conflict_rows ?? 0) > 0;
  const importReady = Boolean(selected && reportCanApply && !hasConflicts && selected.status !== "PREVIEW_ONLY");
  const steps = [
    { label: "Upload", state: latest ? "done" : "pending" },
    { label: "Preview", state: preview ? "done" : latest ? "current" : "pending" },
    { label: "Mapeamento", state: preview ? "current" : "pending" },
    { label: "Validação", state: latest ? "done" : "pending" },
    { label: "Conflitos", state: hasConflicts ? "blocked" : latest ? "done" : "pending" },
    { label: "Aplicar", state: importReady ? "current" : "pending" },
    { label: "Resultado", state: latest?.status?.startsWith("APPLIED") ? "done" : "pending" }
  ];

  return (
    <div className="base44-import-page">
      <Base44PageHeader
        eyebrow="Importações"
        title="Importações"
        description="Fluxo real de upload, preview, staging, mapeamento, validação e aplicação com a experiência Apoema sobre a lógica existente."
        actions={
          <>
            <Base44StatusBadge status={uploading ? "warning" : "auditavel"}>{uploading ? "Enviando" : "Upload ativo"}</Base44StatusBadge>
            <Base44StatusBadge status={importReady ? "success" : "warning"}>{importReady ? "Pronto para aplicar" : "Revisão necessária"}</Base44StatusBadge>
          </>
        }
      />

      <section className="grid base44-import-summary-grid">
        <Base44InfoGrid
          columns={3}
          title="Resumo da importação"
          items={[
            { label: "Última carga", value: latest ? formatDateTime(latest.created_at) : "-", hint: latest?.filename ?? "Nenhum arquivo selecionado." },
            { label: "Linhas válidas", value: latest?.valid_rows ?? 0, hint: "Entradas prontas para revisão ou aplicação." },
            { label: "Linhas com conflito", value: latest?.conflict_rows ?? 0, hint: "Demandam conferência manual antes da decisão." },
            { label: "Linhas inválidas", value: latest?.invalid_rows ?? 0, hint: "Campos obrigatórios ou regras de validação quebradas." },
            { label: "Ações criadas", value: latest?.created_rows ?? 0, hint: "Registros novos preservados após a conferência." },
            { label: "Ações atualizadas", value: latest?.updated_rows ?? 0, hint: "Atualizações confirmadas pelo fluxo real." },
          ]}
        />
        <Base44Surface className="base44-import-status-shell" as="aside">
          <p className="base44-eyebrow">Status do fluxo</p>
          <div className="base44-chip-row">
            <Base44StatusBadge status="auditavel">{latest ? formatTechnicalLabel(latest.status) : "Sem importação"}</Base44StatusBadge>
            <Base44StatusBadge status="auditavel">{page?.total ?? 0} jobs</Base44StatusBadge>
          </div>
          <p className="base44-import-summary-copy">
            O contrato real continua intacto: upload, preview, mapeamento, staging, validação, aplicação e cancelamento seguem chamando a API existente.
          </p>
          <div className="base44-import-step-list">
            {steps.map((step) => <Base44StatusBadge key={step.label} status={step.state === "blocked" ? "danger" : step.state === "current" ? "auditavel" : step.state === "done" ? "success" : "leitura"}>{step.label}</Base44StatusBadge>)}
          </div>
        </Base44Surface>
      </section>

      <Base44ImportPanel
        eyebrow="Upload e modo"
        title="Enviar arquivo para staging"
        description="Escolha o modo, envie o arquivo e mantenha a decisão humana antes de aplicar qualquer alteração operacional."
        actions={<Base44StatusBadge status={uploading ? "warning" : "leitura"}>{uploading ? "Upload em andamento" : "Fluxo controlado"}</Base44StatusBadge>}
      >
        <div className="base44-import-upload-grid">
          <label className={`base44-import-dropzone ${uploading ? "is-disabled" : ""}`}>
            <span className="base44-import-dropzone-icon"><Upload size={18} aria-hidden /></span>
            <strong>{uploading ? "Enviando..." : "Selecionar arquivo"}</strong>
            <small>CSV ou XLSX. Fórmulas perigosas e macros seguem bloqueadas pelo backend.</small>
            <input className="hidden-input" type="file" accept=".csv,.xlsx" onChange={handleFile} disabled={uploading} />
          </label>
          <div className="base44-import-controls">
            <label>
              <span>Modo da importação</span>
              <select className="select" value={importMode} onChange={(event) => setImportMode(event.target.value)}>
                {IMPORT_MODES.map((mode) => (
                  <option value={mode} key={mode}>{mode}</option>
                ))}
              </select>
            </label>
            <p>Ativos existentes não terão usuário, status ou localização sobrescritos automaticamente.</p>
            <div className="base44-import-actions">
              <button className="button" type="button" onClick={applyImport} disabled={!canApply || !reportCanApply || applying}>
                {applying ? "Aplicando..." : "Aplicar importação"}
              </button>
              <button className="button secondary" type="button" onClick={cancelImport} disabled={!canApply}>Cancelar</button>
            </div>
          </div>
        </div>
      </Base44ImportPanel>

      {message ? <Alert tone="success">{message}</Alert> : null}
      {error ? <Alert tone="danger">{error}</Alert> : null}
      {loading ? <LoadingBlock /> : null}

      <section className="grid metrics base44-import-metrics">
        {metrics.map(([label, value, tone]) => (
          <article className={`card metric-card ${tone ? `metric-${tone}` : ""}`} key={label}>
            <div className="metric-label">{label}</div>
            <div className="metric-value">{value}</div>
          </article>
        ))}
      </section>

      <Base44Surface className="base44-import-workspace" as="section">
        <div className="base44-import-workspace-head">
          <div>
            <p className="base44-eyebrow">Fluxo</p>
            <h2>Pipeline de importação</h2>
            <p className="base44-import-workspace-description">Preview, mapeamento e staging continuam visíveis para revisão antes de qualquer apply real.</p>
          </div>
          <div className="base44-chip-row">
            <Base44StatusBadge status={hasConflicts ? "warning" : "success"}>{hasConflicts ? `${latest?.conflict_rows ?? 0} conflitos` : "Sem conflitos"}</Base44StatusBadge>
            <Base44StatusBadge status={warnings.length ? "warning" : "leitura"}>{warnings.length ? `${warnings.length} alertas` : "Sem alertas"}</Base44StatusBadge>
          </div>
        </div>
        <div className="base44-import-stepper">
          {steps.map((step) => (
            <span className={`badge step-${step.state}`} key={step.label}>{step.label}</span>
          ))}
        </div>
        <p><strong>Pronto para aplicar?</strong> {importReady ? "Sim, após confirmação humana." : "Não."}</p>
        <p><strong>O que bloqueia?</strong> {hasConflicts ? `${latest?.conflict_rows ?? 0} conflito(s) exigem revisão.` : blockers.length ? blockers.join(" ") : "Nenhum bloqueio automático identificado."}</p>
        <p><strong>Próxima ação recomendada:</strong> {hasConflicts ? "Abrir conflitos e decidir tratamento antes de aplicar." : importReady ? "Revisar mapeamento final e aplicar com confirmação." : "Concluir upload/preview antes da decisão."}</p>
      </Base44Surface>

      <section className="grid base44-import-detail-grid">
        <Base44Surface className="base44-import-detail-panel" as="article">
          <h2>Importações</h2>
          <DataTable
            items={page?.items ?? []}
            columns={[
              { key: "filename", label: "Arquivo" },
              {
                key: "status",
                label: "Status",
                render: (item) => (
                  <Base44StatusBadge status={item.status === "APPLIED" || item.status === "APPLIED_WITH_ISSUES" ? "success" : item.status === "CANCELLED" ? "leitura" : item.status === "FAILED" ? "danger" : item.status === "PREVIEW_ONLY" ? "leitura" : item.status === "VALIDATED" ? "auditavel" : "warning"}>
                    {formatTechnicalLabel(item.status)}
                  </Base44StatusBadge>
                )
              },
              { key: "total_rows", label: "Linhas" },
              { key: "conflict_rows", label: "Conflitos" },
              { key: "created_at", label: "Criada em", render: (item) => formatDateTime(item.created_at) },
              { key: "id", label: "Ação", render: (item) => <button className="mini-button" type="button" onClick={() => setSelected(item)}>Abrir</button> }
            ]}
          />
        </Base44Surface>

        <Base44Surface className="base44-import-detail-panel" as="article">
          <h2>Mapeamento</h2>
          {!preview ? <Base44EmptyState title="Nenhuma importação selecionada." description="Ao abrir um job, o preview e o mapeamento detectado aparecem aqui." icon={FileUp} /> : null}
          {preview ? (
            <div className="base44-import-mapping-grid">
              {preview.columns.map((column) => (
                <label key={column}>
                  <span>{column}</span>
                  <select className="select" value={mapping[column] ?? ""} onChange={(event) => setMapping((current) => ({ ...current, [column]: event.target.value }))}>
                    <option value="">Ignorar</option>
                    {FIELD_OPTIONS.map((field) => (
                      <option value={field} key={field}>{field}</option>
                    ))}
                  </select>
                </label>
              ))}
              <button className="button secondary" type="button" onClick={saveMapping}>Salvar mapeamento</button>
            </div>
          ) : null}
        </Base44Surface>
      </section>

      <section className="grid base44-import-detail-grid">
        <Base44Surface className="base44-import-detail-panel" as="article">
          <h2>Staging</h2>
          <DataTable
            items={staging?.items ?? []}
            columns={[
              { key: "row_number", label: "Linha" },
              { key: "identity_value", label: "Identificador" },
              { key: "identity_confidence", label: "Confiança" },
              { key: "decision", label: "Ação", render: (item) => <span className="badge">{formatImportDecision(item.decision)}</span> },
              { key: "row_status", label: "Status" },
              { key: "merge_action", label: "Merge" },
              { key: "issues", label: "Motivo", render: (item) => item.issues.map(issueText).join(" ") }
            ]}
          />
        </Base44Surface>

        <Base44Surface className="base44-import-detail-panel" as="article">
          <h2>Erros e conflitos</h2>
          <div className="base44-import-issue-stack">
            <div>
              <h3>Erros</h3>
              <DataTable
                items={validationErrors}
                columns={[
                  { key: "row_number", label: "Linha" },
                  { key: "field_name", label: "Campo" },
                  { key: "error_code", label: "Código" },
                  { key: "message", label: "Mensagem" }
                ]}
              />
            </div>
            <div>
              <h3>Conflitos</h3>
              <DataTable
                items={conflicts}
                columns={[
                  { key: "conflict_type", label: "Tipo" },
                  { key: "severity", label: "Severidade" },
                  { key: "details", label: "Detalhe", render: (item) => conflictText(item) }
                ]}
              />
            </div>
          </div>
        </Base44Surface>
      </section>
    </div>
  );
}
