import { FormEvent, useRef, useState } from "react";
import { Check, Copy, RotateCcw, Search } from "lucide-react";

import { Alert } from "@/components/StateBlocks";
import { Button } from "@/components/ui/button";
import { api, mapAiChatError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { ItilMacroOutput } from "@/lib/types";

const PRACTICES = [
  ["automatic", "Automático"], ["incident", "Incidente"], ["service_request", "Solicitação de serviço"],
  ["problem", "Problema"], ["change", "Mudança"], ["access", "Acesso"], ["other", "Outro"],
];
const fieldClass = "min-h-11 w-full rounded-xl border border-white/10 bg-slate-950/55 px-3 text-sm text-slate-100 outline-none focus:border-cyan-300/50 focus:ring-2 focus:ring-cyan-300/20";

export function MacrosPage() {
  const { token, user } = useAuth();
  const [result, setResult] = useState<ItilMacroOutput | null>(null);
  const [macroText, setMacroText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const controller = useRef<AbortController | null>(null);

  if (user && !["ADMIN", "TECHNICIAN"].includes(user.role)) return <main className="screen-center">Acesso não autorizado.</main>;

  async function generate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    controller.current = new AbortController();
    setLoading(true); setError(null); setCopied(false);
    try {
      const payload = Object.fromEntries([...data].filter(([, value]) => String(value).trim()));
      const output = await api.generateItilMacro(token as string, payload, controller.current.signal);
      setResult(output); setMacroText(output.macro_text);
    } catch (reason) {
      if ((reason as Error).name !== "AbortError") setError(mapAiChatError(reason).message);
    } finally { setLoading(false); controller.current = null; }
  }

  async function copy() { await navigator.clipboard.writeText(macroText); setCopied(true); }

  return (
    <div className="mx-auto grid max-w-6xl gap-6 pb-10">
      <header><h1 className="text-2xl font-semibold text-slate-50">Macros</h1><p className="mt-1 text-sm text-slate-400">Gere registros de atendimento claros e padronizados.</p></header>
      {error ? <Alert tone="danger">{error}</Alert> : null}
      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <form className="grid content-start gap-4 rounded-2xl bg-white/[0.035] p-5" onSubmit={generate}>
          <label className="grid gap-2 text-sm font-medium text-slate-200">Tipo de atendimento<select name="practice" className={fieldClass} defaultValue="automatic">{PRACTICES.map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label>
          <label className="grid gap-2 text-sm font-medium text-slate-200">Resumo do atendimento<textarea name="summary" required minLength={3} rows={5} className={`${fieldClass} py-3`} placeholder="Descreva o pedido, sintoma e impacto conhecido." /></label>
          <label className="grid gap-2 text-sm font-medium text-slate-200">Ação realizada<textarea name="actions_taken" rows={3} className={`${fieldClass} py-3`} /></label>
          <label className="grid gap-2 text-sm font-medium text-slate-200">Resultado<textarea name="result" rows={3} className={`${fieldClass} py-3`} /></label>
          <details className="rounded-xl border border-white/10 p-3"><summary className="cursor-pointer text-sm font-medium text-slate-200">Adicionar detalhes</summary><div className="mt-4 grid gap-4"><label className="grid gap-2 text-sm text-slate-300">Ativo/CI<input name="configuration_item" className={fieldClass} /></label><label className="grid gap-2 text-sm text-slate-300">Usuário ou área<input name="requester" className={fieldClass} /></label><label className="grid gap-2 text-sm text-slate-300">Informações adicionais<textarea name="additional_information" rows={3} className={`${fieldClass} py-3`} /></label></div></details>
          <div className="flex flex-wrap gap-2"><Button type="submit" disabled={loading} className="min-h-11 bg-cyan-400 text-slate-950 hover:bg-cyan-300">{loading ? "Analisando atendimento…" : "Gerar macro com Hermes"}</Button>{loading ? <Button type="button" variant="outline" className="min-h-11" onClick={()=>controller.current?.abort()}>Cancelar</Button> : null}</div>
        </form>
        <section className="min-w-0 rounded-2xl bg-white/[0.035] p-5" aria-live="polite">
          <div className="flex items-center justify-between gap-3"><h2 className="text-lg font-semibold text-slate-50">Preview</h2>{result ? <span className="text-sm text-slate-400">{result.practice.replaceAll("_", " ")} · {result.priority}</span> : null}</div>
          {!result ? <div className="grid min-h-72 place-items-center text-center text-sm text-slate-500"><div><Search className="mx-auto mb-3 h-6 w-6"/><p>Preencha o atendimento para gerar a macro.</p></div></div> : <div className="mt-4 grid gap-4">
            {result.missing_information.length ? <Alert tone="warning">Campos ausentes: {result.missing_information.join(", ")}</Alert> : null}
            {result.warnings.length ? <Alert tone="warning">{result.warnings.join(" ")}</Alert> : null}
            <textarea aria-label="Macro gerada editável" value={macroText} onChange={(e)=>{setMacroText(e.target.value);setCopied(false);}} rows={16} className={`${fieldClass} min-h-80 py-3 leading-6`} />
            <div className="flex flex-wrap gap-2"><Button type="button" onClick={copy} className="min-h-11 bg-cyan-400 text-slate-950 hover:bg-cyan-300">{copied ? <Check className="mr-2 h-4 w-4"/> : <Copy className="mr-2 h-4 w-4"/>}{copied ? "Copiada" : "Copiar"}</Button><Button type="button" variant="outline" className="min-h-11" onClick={()=>setResult(null)}><RotateCcw className="mr-2 h-4 w-4"/>Editar atendimento</Button></div>
          </div>}
        </section>
      </div>
      <details className="border-t border-white/10 pt-4"><summary className="cursor-pointer text-sm font-medium text-slate-300">Histórico e templates</summary><p className="mt-3 text-sm text-slate-500">O histórico oficial de movimentações permanece disponível no fluxo do ativo.</p></details>
    </div>
  );
}
