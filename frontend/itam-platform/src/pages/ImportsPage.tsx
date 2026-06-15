import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { DataTable } from "@/components/DataTable";
import { HermesStatusPill } from "@/components/brand/HermesStatusPill";
import { SentinelSectionHeader } from "@/components/brand/SentinelSectionHeader";
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
      setError("Falha no upload. Verifique extensao, tamanho, formulas e permissoes.");
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
    <>
      <SentinelSectionHeader
        eyebrow="Importação Lansweeper"
        subtitle="Pipeline com etapas, conflitos e validação antes de aplicar mudanças."
        title="Importação Lansweeper"
      />
      <section className="grid import-export-grid">
        <article className="card import-card">
          <h2>Importar Planilha Excel</h2>
          <p>Faça upload de arquivo CSV/XLSX. A aplicação só ocorre após revisão do preview, mapeamento, validação e conflitos.</p>
          <label className={`dropzone ${uploading ? "disabled" : ""}`}>
            <span className="dropzone-icon">Arquivo</span>
            <strong>{uploading ? "Enviando..." : "Clique para selecionar o arquivo"}</strong>
            <small>Suporta CSV/XLSX. Fórmulas perigosas e macros são bloqueadas.</small>
            <input className="hidden-input" type="file" accept=".csv,.xlsx" onChange={handleFile} disabled={uploading} />
          </label>
        </article>
        <article className="card export-card">
          <h2>Exportar Dados</h2>
          <p>Exportação consolidada ainda será tratada em fluxo próprio. Use filtros das telas operacionais nesta versão.</p>
          <button className="button secondary" type="button" disabled title="Exportação ainda não disponível nesta versão">Exportação em preparação</button>
        </article>
      </section>

      <section className="card">
        <h2>Modo da importação</h2>
        <div className="action-bar">
          <select className="select" value={importMode} onChange={(event) => setImportMode(event.target.value)}>
            {IMPORT_MODES.map((mode) => (
              <option value={mode} key={mode}>{mode}</option>
            ))}
          </select>
          <p>Ativos existentes não terão usuário, status ou localização sobrescritos automaticamente.</p>
        </div>
      </section>

      {message ? <Alert tone="success">{message}</Alert> : null}
      {error ? <Alert tone="danger">{error}</Alert> : null}
      {loading ? <LoadingBlock /> : null}

      <section className="grid metrics">
        {metrics.map(([label, value, tone]) => (
          <article className={`card metric-card ${tone ? `metric-${tone}` : ""}`} key={label}>
            <div className="metric-label">{label}</div>
            <div className="metric-value">{value}</div>
          </article>
        ))}
      </section>

      <section className="card">
        <h2>Fluxo da importação</h2>
        <div className="pipeline-strip stepper">
          {steps.map((step) => (
            <span className={`badge step-${step.state}`} key={step.label}>{step.label}</span>
          ))}
        </div>
      </section>

      <section className="card decision-panel">
        <h2>Decisão da importação</h2>
        <p><strong>Pronto para aplicar?</strong> {importReady ? "Sim, após confirmação humana." : "Não."}</p>
        <p><strong>O que bloqueia?</strong> {hasConflicts ? `${latest?.conflict_rows} conflito(s) exigem revisão.` : blockers.length ? blockers.join(" ") : "Nenhum bloqueio automático identificado."}</p>
        <p><strong>Próxima ação recomendada:</strong> {hasConflicts ? "Abrir conflitos e decidir tratamento antes de aplicar." : importReady ? "Revisar mapeamento final e aplicar com confirmação." : "Concluir upload/preview antes da decisão."}</p>
      </section>

      <section className="grid detail-grid">
        <article className="card">
          <h2>Preset e qualidade</h2>
          <p><strong>Preset:</strong> {report.preset_name ? String(report.preset_name) : "Preset não detectado. Revise o mapeamento antes de aplicar."}</p>
          <p><strong>Versão:</strong> {String(report.preset_version ?? "-")}</p>
          <p><strong>Aba:</strong> {String(report.detected_sheet ?? "-")}</p>
          <p><strong>Modo:</strong> {String(report.import_mode ?? importMode)}</p>
          {warnings.map((warning) => <Alert key={warning}>{warning}</Alert>)}
          <div className="grid metrics compact">
            {[
              ["Com serial", summary.rows_with_valid_serial ?? 0],
              ["Sem serial", summary.rows_without_valid_serial ?? 0],
              ["Com hostname", summary.rows_with_hostname ?? 0],
              ["Sem patrimônio", summary.rows_without_patrimony ?? 0],
              ["Tipo reconhecido", summary.rows_with_recognized_type ?? 0],
              ["Status reconhecido", summary.rows_with_recognized_status ?? 0]
            ].map(([label, value]) => (
              <article className="card" key={String(label)}>
                <div className="metric-label">{label}</div>
                <div className="metric-value">{value}</div>
              </article>
            ))}
          </div>
          <p>Serial válido: {quality.pct_with_valid_serial ?? 0}% | Hostname: {quality.pct_with_hostname ?? 0}% | Sem patrimônio: {quality.pct_without_patrimony ?? 0}%</p>
        </article>
        <article className="card">
          <h2>Distribuicoes</h2>
          {(["state", "custom1", "asset_family", "building"] as const).map((key) => (
            <div key={key}>
              <h3>{key}</h3>
              <p>{Object.entries(distributions[key] ?? {}).slice(0, 8).map(([name, count]) => `${name}: ${count}`).join(" | ") || "Sem dados"}</p>
            </div>
          ))}
        </article>
      </section>

      <section className="grid detail-grid">
        <article className="card">
          <h2>Importacoes</h2>
          <DataTable
            items={page?.items ?? []}
            columns={[
              { key: "filename", label: "Arquivo" },
              {
                key: "status",
                label: "Status",
                render: (item) => (
                  <HermesStatusPill
                    state={
                      item.status === "APPLIED" || item.status === "APPLIED_WITH_ISSUES"
                        ? "Validado"
                        : item.status === "CANCELLED"
                          ? "Somente leitura"
                          : item.status === "FAILED"
                            ? "Erro"
                            : item.status === "PREVIEW_ONLY"
                              ? "Somente leitura"
                              : item.status === "VALIDATED"
                                ? "Auditável"
                                : "Em revisão"
                    }
                  >
                    {formatTechnicalLabel(item.status)}
                  </HermesStatusPill>
                )
              },
              { key: "total_rows", label: "Linhas" },
              { key: "conflict_rows", label: "Conflitos" },
              { key: "created_at", label: "Criada em", render: (item) => formatDateTime(item.created_at) },
              { key: "id", label: "Ação", render: (item) => <button className="mini-button" onClick={() => setSelected(item)}>Abrir</button> }
            ]}
          />
        </article>

        <article className="card">
          <h2>Mapeamento</h2>
          {!preview ? <p>Nenhuma importação selecionada.</p> : null}
          {preview ? (
            <div className="mapping-grid">
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
              <button className="button secondary" onClick={saveMapping}>Salvar mapeamento</button>
            </div>
          ) : null}
        </article>
      </section>

      <section className="card">
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
      </section>

      <section className="grid detail-grid">
        <article className="card">
          <h2>Erros</h2>
          <DataTable
            items={validationErrors}
            columns={[
              { key: "row_number", label: "Linha" },
              { key: "field_name", label: "Campo" },
              { key: "error_code", label: "Código" },
              { key: "message", label: "Mensagem" }
            ]}
          />
        </article>
        <article className="card">
          <h2>Conflitos</h2>
          <DataTable
            items={conflicts}
            columns={[
              { key: "conflict_type", label: "Tipo" },
              { key: "severity", label: "Severidade" },
              { key: "details", label: "Detalhe", render: (item) => conflictText(item) }
            ]}
          />
        </article>
      </section>

      <section className="card action-bar">
        <p>Campos protegidos não são sobrescritos automaticamente: usuário atual, status, localização, observações e histórico.</p>
        <div>
          <button className="button" onClick={applyImport} disabled={!canApply || !reportCanApply || applying}>
            {applying ? "Aplicando..." : "Aplicar importação"}
          </button>
          <button className="button secondary" onClick={cancelImport} disabled={!canApply}>Cancelar</button>
        </div>
      </section>
    </>
  );
}

