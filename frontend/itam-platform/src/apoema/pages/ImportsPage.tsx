import { ChangeEvent, DragEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import { Check, ChevronDown, FileSpreadsheet, Upload } from "lucide-react";

import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Button } from "@/components/ui/button";
import { api, mapAiChatError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { ImportAiAnalysis, ImportCorrection, ImportJob, ImportPreview } from "@/lib/types";

const IMPORT_AI_TIMEOUT_MS = 125000;

function displayValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "—";
  return typeof value === "object" ? JSON.stringify(value) : String(value);
}

export function ImportsPage() {
  const { token, user } = useAuth();
  const input = useRef<HTMLInputElement>(null);
  const [job, setJob] = useState<ImportJob | null>(null);
  const [analysis, setAnalysis] = useState<ImportAiAnalysis | null>(null);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [suggestions, setSuggestions] = useState<ImportCorrection[]>([]);
  const [busy, setBusy] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    api.imports(token).then((page) => {
      const latest = page.items[0] ?? null;
      setJob(latest);
      if (latest) void api.aiSuggestions(token, latest.id).then(setSuggestions).catch(() => undefined);
    }).catch(() => undefined);
  }, [token]);

  async function analyze(nextJob: ImportJob) {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), IMPORT_AI_TIMEOUT_MS);
    try {
      const [result, nextPreview] = await Promise.all([api.analyzeImport(token as string, nextJob.id, controller.signal), api.importPreview(token as string, nextJob.id)]);
      setAnalysis(result); setPreview(nextPreview); setSuggestions(result.ai_suggestions);
    } finally {
      window.clearTimeout(timeout);
    }
  }

  async function upload(file: File) {
    setBusy(true); setError(null); setMessage(null); setAnalysis(null); setPreview(null); setSuggestions([]);
    try {
      const nextJob = await api.importUpload(token as string, file, "INITIAL_LOAD");
      setJob(nextJob); await analyze(nextJob);
      setMessage("Análise concluída. Revise as pendências antes de importar.");
    } catch (reason) { setError(reason instanceof DOMException && reason.name === "AbortError" ? "A análise excedeu 125 segundos. Nenhuma sugestão foi aplicada." : mapAiChatError(reason).message); }
    finally { setBusy(false); }
  }

  async function onFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]; if (file) await upload(file); event.target.value = "";
  }
  function onDrop(event: DragEvent<HTMLLabelElement>) { event.preventDefault(); setDragActive(false); const file=event.dataTransfer.files?.[0]; if(file&&!busy) void upload(file); }
  function onKey(event: KeyboardEvent<HTMLLabelElement>) { if(!busy&&(event.key==="Enter"||event.key===" ")){event.preventDefault();input.current?.click();} }

  async function apply() {
    if (!job || !analysis?.safe_to_apply || !window.confirm("Confirmar importação após revisão humana?")) return;
    setBusy(true); setError(null);
    try { const result=await api.applyImport(token as string,job.id); setJob(result.job); setMessage("Importação aplicada com auditoria."); }
    catch(reason){setError(mapAiChatError(reason).message);} finally{setBusy(false);}
  }

  async function decideSuggestion(item: ImportCorrection, decision: "APPROVED" | "REJECTED") {
    if (!job || !item.id) return;
    setBusy(true); setError(null);
    try {
      const updated = decision === "APPROVED"
        ? await api.approveAiSuggestion(token as string, job.id, item.id)
        : await api.rejectAiSuggestion(token as string, job.id, item.id);
      setSuggestions((current) => current.map((candidate) => candidate.id === updated.id ? updated : candidate));
      setMessage(decision === "APPROVED" ? "Sugestão aprovada e auditada. Nenhuma alteração foi aplicada automaticamente." : "Sugestão rejeitada e auditada.");
    } catch (reason) { setError(mapAiChatError(reason).message); }
    finally { setBusy(false); }
  }

  const summary=analysis?.file_summary;
  const canDecide = user?.role === "ADMIN" || user?.role === "TECHNICIAN";
  return <div className="mx-auto grid max-w-5xl gap-6 pb-10">
    <header><h1 className="text-2xl font-semibold text-slate-50">Importar ativos</h1><p className="mt-1 text-sm text-slate-400">Envie uma planilha. A IA identifica colunas, corrige formatos e mostra o que precisa de revisão.</p></header>
    {message?<Alert tone="success">{message}</Alert>:null}{error?<Alert tone="danger">{error}</Alert>:null}
    <label data-testid="imports-dropzone" role="button" tabIndex={busy?-1:0} aria-disabled={busy} aria-label="Selecionar ou arrastar planilha" onKeyDown={onKey} onDrop={onDrop} onDragOver={(e)=>{e.preventDefault();setDragActive(true);}} onDragLeave={()=>setDragActive(false)} className={`grid min-h-72 cursor-pointer place-items-center rounded-2xl border border-dashed p-8 text-center outline-none transition-colors focus-visible:ring-2 focus-visible:ring-cyan-300 ${dragActive?"border-cyan-300 bg-cyan-400/10":"border-white/15 bg-white/[0.025] hover:border-cyan-300/40"}`}>
      <div><span className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-cyan-400/10 text-cyan-200"><Upload className="h-6 w-6"/></span><strong className="text-base text-slate-100">{busy?"Analisando planilha…":dragActive?"Solte para analisar":"Arraste a planilha aqui"}</strong><p className="mt-2 text-sm text-slate-500">CSV ou XLSX · limites definidos pelo servidor</p><span className="mt-5 inline-flex min-h-11 items-center rounded-xl bg-cyan-400 px-5 text-sm font-semibold text-slate-950">Selecionar planilha</span><input ref={input} className="sr-only" type="file" accept=".csv,.xlsx" disabled={busy} onChange={onFile}/></div>
    </label>
    {busy?<LoadingBlock/>:null}
    {summary?<section className="grid gap-5 rounded-2xl bg-white/[0.035] p-5">
      <div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-lg font-semibold text-slate-50">Resumo da análise</h2><p className="mt-1 text-sm text-slate-400">{summary.rows_need_review?`Existem ${summary.rows_need_review} itens que precisam da sua confirmação.`:"Planilha pronta para importar."}</p></div><FileSpreadsheet className="h-5 w-5 text-cyan-200"/></div>
      <dl className="grid grid-cols-2 gap-4 sm:grid-cols-5"><div><dt className="text-xs text-slate-500">Status</dt><dd className="mt-1 text-sm font-semibold text-cyan-100">{job?.status??"—"}</dd></div><div><dt className="text-xs text-slate-500">Linhas</dt><dd className="mt-1 text-xl text-slate-100">{summary.rows_total}</dd></div><div><dt className="text-xs text-slate-500">Corrigidas</dt><dd className="mt-1 text-xl text-slate-100">{summary.rows_auto_corrected}</dd></div><div><dt className="text-xs text-slate-500">Revisão</dt><dd className="mt-1 text-xl text-amber-100">{summary.rows_need_review}</dd></div><div><dt className="text-xs text-slate-500">Inválidas</dt><dd className="mt-1 text-xl text-rose-100">{summary.rows_invalid}</dd></div></dl>
      <div className="flex flex-wrap gap-2">{summary.rows_need_review?<Button type="button" variant="outline" className="min-h-11" onClick={()=>document.getElementById("ai-suggestions")?.scrollIntoView({behavior:"smooth"})}>Revisar pendências</Button>:null}<Button type="button" className="min-h-11 bg-cyan-400 text-slate-950 hover:bg-cyan-300" disabled={!analysis.safe_to_apply||busy} onClick={apply}><Check className="mr-2 h-4 w-4"/>Importar</Button><Button type="button" variant="ghost" className="min-h-11" onClick={()=>{setJob(null);setAnalysis(null);setPreview(null);setSuggestions([]);}}>Cancelar</Button></div>
    </section>:null}
    {suggestions.length?<section id="ai-suggestions" className="grid gap-4 rounded-2xl border border-amber-300/15 bg-amber-300/[0.035] p-5"><div><h2 className="text-lg font-semibold text-slate-50">Sugestões da IA</h2><p className="mt-1 text-sm text-slate-400">Painel separado para decisão humana. Aprovar não altera o staging nem aplica a importação.</p></div>{suggestions.map((item)=><article key={item.id??`${item.row}-${item.field}`} className="grid gap-3 rounded-xl border border-white/10 bg-slate-950/35 p-4"><div className="flex flex-wrap items-center justify-between gap-2"><strong className="text-sm text-slate-100">Linha {item.row} · {item.field}</strong><span className="rounded-full border border-white/10 px-2 py-1 text-xs text-slate-300">{item.status??"PENDING"}</span></div><dl className="grid gap-3 sm:grid-cols-2"><div><dt className="text-xs text-slate-500">Valor atual</dt><dd className="mt-1 break-words text-sm text-slate-200">{displayValue(item.original_value)}</dd></div><div><dt className="text-xs text-slate-500">Sugestão</dt><dd className="mt-1 break-words text-sm text-cyan-100">{displayValue(item.proposed_value)}</dd></div><div><dt className="text-xs text-slate-500">Confiança</dt><dd className="mt-1 text-sm text-slate-200">{Math.round(item.confidence*100)}%</dd></div><div><dt className="text-xs text-slate-500">Motivo</dt><dd className="mt-1 text-sm text-slate-200">{item.reason}</dd></div></dl>{item.status==="PENDING"?<div className="flex flex-wrap gap-2"><Button type="button" className="min-h-11 bg-cyan-400 text-slate-950 hover:bg-cyan-300" disabled={!canDecide||busy} onClick={()=>void decideSuggestion(item,"APPROVED")}>Aprovar</Button><Button type="button" variant="outline" className="min-h-11" disabled={!canDecide||busy} onClick={()=>void decideSuggestion(item,"REJECTED")}>Rejeitar</Button>{!canDecide?<span className="self-center text-xs text-slate-500">VIEWER não pode decidir sugestões.</span>:null}</div>:null}</article>)}</section>:null}
    <details id="import-details" className="border-t border-white/10 pt-4"><summary className="flex cursor-pointer list-none items-center justify-between text-sm font-medium text-slate-300">Opções avançadas e detalhes<ChevronDown className="h-4 w-4"/></summary><div className="mt-4 grid gap-4 text-sm text-slate-400"><p>Arquivo: {job?.filename??"Nenhum"}</p><p>Confiança da análise: {analysis?`${Math.round(analysis.confidence*100)}%`:"—"}</p>{preview?<p>{preview.items.length} linhas disponíveis no preview técnico.</p>:null}</div></details>
  </div>;
}
