import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { FileUp, Upload, ChevronDown } from "lucide-react";

import { DataTable } from "@/components/DataTable";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Button } from "@/components/ui/button";
import { DonorChip, DonorField, DonorFieldGrid, DonorSelect } from "../components/DonorForm";
import { DonorPanelPageLayout } from "../components/DonorPanelPageLayout";
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
  "source_metadata.source",
];

const IMPORT_MODES = ["INITIAL_LOAD", "SAFE_REIMPORT", "PREVIEW_ONLY"];

function issueText(issue: Record<string, unknown>) {
  return String(issue.message ?? issue.suggested_action ?? issue.code ?? "Sem detalhe.");
}

function renderIssueChips(issues: Array<Record<string, unknown>>) {
  if (issues.length === 0) {
    return <span className="text-slate-500">Sem detalhes.</span>;
  }
  return (
    <div className="flex min-w-0 flex-wrap gap-2">
      {issues.map((issue, index) => {
        const text = issueText(issue);
        return (
          <DonorChip key={`${text}-${index}`} className="max-w-full whitespace-normal break-words text-left">
            {text}
          </DonorChip>
        );
      })}
    </div>
  );
}

function renderConflictDetails(conflict: ImportConflict) {
  const details = conflict.details ?? {};
  const identity = [details.identity_type, details.identity_value].filter(Boolean).join(" · ");
  const rows = Array.isArray(details.rows) ? details.rows.join(", ") : "";
  return (
    <div className="grid min-w-0 gap-2">
      <strong className="break-words text-sm text-slate-50">{String(details.message ?? conflict.conflict_type)}</strong>
      <div className="flex min-w-0 flex-wrap gap-2">
        <DonorChip className="max-w-full whitespace-normal break-words">{conflict.conflict_type}</DonorChip>
        <DonorChip className="max-w-full whitespace-normal break-words">{conflict.severity}</DonorChip>
        {identity ? <DonorChip className="max-w-full whitespace-normal break-words">{identity}</DonorChip> : null}
        {rows ? <DonorChip className="max-w-full whitespace-normal break-words">{`Linhas ${rows}`}</DonorChip> : null}
      </div>
      {details.suggested_action ? <p className="break-words text-xs leading-5 text-slate-400">Ação sugerida: {details.suggested_action as string}</p> : null}
    </div>
  );
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
      api.importValidationErrors(token, job.id),
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
      setMessage("Arquivo enviado para staging. Revise o resumo e os detalhes avançados antes de aplicar.");
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

  function requestHermesCorrection() {
    setMessage("Hermes precisa de endpoint de correção de planilha configurado para aplicar sugestões automaticamente. O resumo e os detalhes avançados permanecem disponíveis para revisão humana.");
    setError(null);
  }

  const latest = selected ?? page?.items[0];
  const report = (latest?.report ?? {}) as Record<string, unknown>;
  const warnings = Array.isArray(report.warnings) ? report.warnings.map(String) : [];
  const blockers = Array.isArray(report.apply_blockers) ? report.apply_blockers.map(String) : [];
  const hasConflicts = (latest?.conflict_rows ?? 0) > 0;
  const reportCanApply = selected ? selected.report.can_apply !== false : false;
  const importReady = Boolean(selected && reportCanApply && !hasConflicts && selected.status !== "PREVIEW_ONLY");
  const steps = [
    { label: "Upload", state: latest ? "done" : "pending" },
    { label: "Preview", state: preview ? "done" : latest ? "current" : "pending" },
    { label: "Mapeamento", state: preview ? "current" : "pending" },
    { label: "Validação", state: latest ? "done" : "pending" },
    { label: "Conflitos", state: hasConflicts ? "blocked" : latest ? "done" : "pending" },
    { label: "Aplicar", state: importReady ? "current" : "pending" },
    { label: "Resultado", state: latest?.status?.startsWith("APPLIED") ? "done" : "pending" },
  ];

  const metrics = useMemo(
    () => [
      ["Total de linhas", latest?.total_rows ?? 0, ""],
      ["Prontas para aplicar", latest?.valid_rows ?? 0, "success"],
      ["Exigem revisão", (latest?.conflict_rows ?? 0) + (latest?.invalid_rows ?? 0), "warning"],
      ["Inválidas", latest?.invalid_rows ?? 0, latest?.invalid_rows ? "danger" : ""],
      ["Conflitos", latest?.conflict_rows ?? 0, latest?.conflict_rows ? "danger" : ""],
    ],
    [latest],
  );

  return (
    <DonorPanelPageLayout
      eyebrow="Importações"
      title="Importar planilha"
      description="Upload, análise e correção assistida pelo Hermes. Os detalhes técnicos permanecem disponíveis, mas não dominam a tela principal."
      actions={
        <>
          <DonorChip>{uploading ? "Enviando" : "Upload ativo"}</DonorChip>
          <DonorChip>{importReady ? "Pronto para aplicar" : "Revisão necessária"}</DonorChip>
        </>
      }
      stats={[
        { label: "Última carga", value: latest ? formatDateTime(latest.created_at) : "-", detail: latest?.filename ?? "Nenhum arquivo selecionado." },
        { label: "Linhas válidas", value: latest?.valid_rows ?? 0, detail: "Entradas prontas para revisão ou aplicação." },
        { label: "Conflitos", value: latest?.conflict_rows ?? 0, detail: "Demandam conferência antes da decisão." },
        { label: "Inválidas", value: latest?.invalid_rows ?? 0, detail: "Campos obrigatórios ou regras quebradas." },
      ]}
    >
      {message ? <Alert tone="success">{message}</Alert> : null}
      {error ? <Alert tone="danger">{error}</Alert> : null}
      {loading ? <LoadingBlock /> : null}

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)]">
        <section className="rounded-[26px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_50px_-26px_rgba(0,0,0,0.8)]">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Upload</p>
              <h2 className="mt-2 text-lg font-semibold text-slate-50">Enviar planilha para staging</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">Escolha o modo, envie o arquivo e mantenha a decisão humana antes de aplicar qualquer alteração operacional.</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {steps.map((step) => (
                <DonorChip key={step.label} className={step.state === "blocked" ? "border-rose-400/20 bg-rose-500/10 text-rose-100" : step.state === "current" ? "border-cyan-300/20 bg-cyan-400/10 text-cyan-100" : step.state === "done" ? "border-emerald-400/20 bg-emerald-500/10 text-emerald-100" : ""}>
                  {step.label}
                </DonorChip>
              ))}
            </div>
          </div>

          <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(240px,320px)_minmax(0,1fr)]">
            <label className={`grid cursor-pointer gap-3 rounded-[22px] border border-dashed border-white/15 bg-slate-950/40 p-4 transition-colors ${uploading ? "opacity-70" : "hover:border-cyan-300/30 hover:bg-cyan-400/10"}`}>
              <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-100">
                <Upload className="h-5 w-5" />
              </span>
              <div className="grid min-w-0 gap-1">
                <strong className="block break-words text-sm text-slate-50">{uploading ? "Enviando..." : "Selecionar arquivo"}</strong>
                <small className="block max-w-full break-words text-sm leading-6 text-slate-300">CSV ou XLSX. Fórmulas perigosas e macros seguem bloqueadas pelo backend.</small>
              </div>
              <input className="sr-only" type="file" accept=".csv,.xlsx" onChange={handleFile} disabled={uploading} />
            </label>

            <div className="grid min-w-0 gap-4">
              <DonorFieldGrid className="grid-cols-1 lg:grid-cols-2">
                <DonorSelect
                  label="Modo da importação"
                  value={importMode}
                  options={IMPORT_MODES.map((mode) => ({ value: mode, label: formatTechnicalLabel(mode) }))}
                  onChange={setImportMode}
                />
                <DonorField label="Estado do fluxo" hint="O backend real valida, aplica e registra auditoria. Nenhum fake success é exibido.">
                  <div className="flex flex-wrap gap-2">
                    <DonorChip>{latest ? formatTechnicalLabel(latest.status) : "Sem importação"}</DonorChip>
                    <DonorChip>{page?.total ?? 0} jobs</DonorChip>
                  </div>
                </DonorField>
              </DonorFieldGrid>

              <DonorField label="Orientação operacional" hint="Revise preview, mapeamento e conflitos antes de aplicar.">
                <p className="min-w-0 break-words text-sm leading-6 text-slate-300">
                  O fluxo principal continua simples: upload, análise, revisão e aplicação. Os detalhes técnicos ficam recolhidos para consulta.
                </p>
              </DonorField>

              <div className="flex flex-wrap gap-2">
                <Button className="rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300" type="button" onClick={requestHermesCorrection} disabled={!selected}>
                  Analisar e corrigir com Hermes
                </Button>
                <Button className="rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300" type="button" onClick={applyImport} disabled={!selected || !reportCanApply || applying}>
                  {applying ? "Aplicando..." : "Aplicar importação"}
                </Button>
                <Button className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10" type="button" variant="outline" onClick={cancelImport} disabled={!selected}>
                  Cancelar
                </Button>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-[26px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_50px_-26px_rgba(0,0,0,0.8)]">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Resumo</p>
              <h2 className="mt-2 text-lg font-semibold text-slate-50">Próxima ação recomendada</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">O painel mostra a decisão atual sem transformar a tela em um painel técnico cru.</p>
            </div>
            <DonorChip>{hasConflicts ? `${latest?.conflict_rows ?? 0} conflitos` : "Sem conflitos"}</DonorChip>
          </div>

          <div className="mt-5 space-y-3">
            <div className="rounded-[22px] border border-white/10 bg-slate-950/45 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Pronto para aplicar?</p>
              <p className="mt-2 text-sm leading-6 text-slate-300">{importReady ? "Sim, após confirmação humana." : "Não."}</p>
            </div>
            <div className="rounded-[22px] border border-white/10 bg-slate-950/45 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Bloqueios</p>
              <p className="mt-2 break-words text-sm leading-6 text-slate-300">{hasConflicts ? `${latest?.conflict_rows ?? 0} conflito(s) exigem revisão.` : blockers.length ? blockers.join(" ") : "Nenhum bloqueio automático identificado."}</p>
            </div>
            <div className="rounded-[22px] border border-white/10 bg-slate-950/45 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Próxima ação</p>
              <p className="mt-2 break-words text-sm leading-6 text-slate-300">
                {hasConflicts ? "Abrir detalhes avançados e decidir o tratamento antes de aplicar." : importReady ? "Revisar mapeamento final e aplicar com confirmação." : "Concluir upload/preview antes da decisão."}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              {warnings.length ? <DonorChip>{warnings.length} alertas</DonorChip> : <DonorChip>Sem alertas</DonorChip>}
              <DonorChip>{latest?.filename ?? "Nenhum arquivo"}</DonorChip>
            </div>
          </div>
        </section>
      </div>

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map(([label, value, tone]) => (
          <article key={label} className="rounded-[22px] border border-white/10 bg-white/[0.04] p-4 shadow-[0_12px_30px_-24px_rgba(0,0,0,0.75)]">
            <p className="text-xs uppercase tracking-[0.22em] text-slate-500">{label}</p>
            <p className={`mt-2 text-2xl font-semibold text-slate-50 ${tone === "danger" ? "text-rose-100" : tone === "warning" ? "text-amber-100" : tone === "success" ? "text-emerald-100" : ""}`}>{value}</p>
            <p className="mt-2 text-sm leading-6 text-slate-400">Resumo operacional da importação selecionada.</p>
          </article>
        ))}
      </section>

      <details className="rounded-[26px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_50px_-26px_rgba(0,0,0,0.8)]">
        <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-lg font-semibold text-slate-50">
          Detalhes avançados
          <ChevronDown className="h-4 w-4 shrink-0 text-slate-400" />
        </summary>

        <div className="mt-5 space-y-5">
          <section className="rounded-[22px] border border-white/10 bg-slate-950/35 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-200/70">Jobs</p>
                <h3 className="mt-1 text-base font-semibold text-slate-50">Importações recentes</h3>
              </div>
              <DonorChip>{page?.total ?? 0} jobs</DonorChip>
            </div>
            <div className="mt-4 overflow-hidden rounded-[18px] border border-white/10">
              <DataTable
                items={page?.items ?? []}
                columns={[
                  { key: "filename", label: "Arquivo", className: "min-w-0 break-words" },
                  {
                    key: "status",
                    label: "Status",
                    render: (item) => <DonorChip>{formatTechnicalLabel(item.status)}</DonorChip>,
                  },
                  { key: "total_rows", label: "Linhas" },
                  { key: "conflict_rows", label: "Conflitos" },
                  { key: "created_at", label: "Criada em", render: (item) => formatDateTime(item.created_at) },
                  { key: "id", label: "Ação", render: (item) => <Button type="button" variant="outline" className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10" onClick={() => setSelected(item)}>Abrir</Button> },
                ]}
              />
            </div>
          </section>

          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <section className="rounded-[22px] border border-white/10 bg-slate-950/35 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-200/70">Mapeamento</p>
                  <h3 className="mt-1 text-base font-semibold text-slate-50">Campos detectados</h3>
                </div>
                <DonorChip>{preview ? "Carregado" : "Sem preview"}</DonorChip>
              </div>
              {!preview ? (
                <div className="mt-4">
                  <Base44EmptyState title="Nenhuma importação selecionada." description="Ao abrir um job, o preview e o mapeamento detectado aparecem aqui." icon={FileUp} />
                </div>
              ) : (
                <div className="mt-4 grid gap-3 lg:grid-cols-2 xl:grid-cols-3">
                  {preview.columns.map((column) => (
                    <DonorSelect
                      key={column}
                      label={column}
                      placeholder="Ignorar"
                      value={mapping[column] ?? ""}
                      options={[{ value: "", label: "Ignorar" }, ...FIELD_OPTIONS.map((field) => ({ value: field, label: field }))]}
                      onChange={(value) => setMapping((current) => ({ ...current, [column]: value }))}
                    />
                  ))}
                  <div className="lg:col-span-2 xl:col-span-3 flex justify-start">
                    <Button type="button" className="rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300" onClick={saveMapping}>Salvar mapeamento</Button>
                  </div>
                </div>
              )}
            </section>

            <section className="rounded-[22px] border border-white/10 bg-slate-950/35 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-200/70">Staging</p>
                  <h3 className="mt-1 text-base font-semibold text-slate-50">Preview operacional</h3>
                </div>
                <DonorChip>{staging?.items.length ?? 0} linha(s)</DonorChip>
              </div>
              <div className="mt-4 overflow-hidden rounded-[18px] border border-white/10">
                <DataTable
                  items={staging?.items ?? []}
                  columns={[
                    { key: "row_number", label: "Linha" },
                    { key: "identity_value", label: "Identificador" },
                    { key: "identity_confidence", label: "Confiança" },
                    { key: "decision", label: "Ação", render: (item) => <DonorChip>{formatImportDecision(item.decision)}</DonorChip> },
                    { key: "row_status", label: "Status" },
                    { key: "merge_action", label: "Merge" },
                    { key: "issues", label: "Motivo", render: (item) => renderIssueChips(item.issues) },
                  ]}
                />
              </div>
            </section>
          </div>

          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <section className="rounded-[22px] border border-white/10 bg-slate-950/35 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-200/70">Erros</p>
                  <h3 className="mt-1 text-base font-semibold text-slate-50">Validação</h3>
                </div>
                <DonorChip>{validationErrors.length} erro(s)</DonorChip>
              </div>
              <div className="mt-4 overflow-hidden rounded-[18px] border border-white/10">
                <DataTable
                  items={validationErrors}
                  columns={[
                    { key: "row_number", label: "Linha" },
                    { key: "field_name", label: "Campo" },
                    { key: "error_code", label: "Código" },
                    { key: "message", label: "Mensagem", className: "min-w-0 break-words", render: (item) => <span className="break-words leading-6 text-slate-100">{item.message}</span> },
                  ]}
                />
              </div>
            </section>

            <section className="rounded-[22px] border border-white/10 bg-slate-950/35 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-200/70">Conflitos</p>
                  <h3 className="mt-1 text-base font-semibold text-slate-50">Ocorrências</h3>
                </div>
                <DonorChip>{conflicts.length} conflito(s)</DonorChip>
              </div>
              <div className="mt-4 overflow-hidden rounded-[18px] border border-white/10">
                <DataTable
                  items={conflicts}
                  columns={[
                    { key: "conflict_type", label: "Tipo" },
                    { key: "severity", label: "Severidade" },
                    { key: "details", label: "Detalhe", className: "min-w-0 break-words", render: (item) => renderConflictDetails(item) },
                  ]}
                />
              </div>
            </section>
          </div>
        </div>
      </details>
    </DonorPanelPageLayout>
  );
}
