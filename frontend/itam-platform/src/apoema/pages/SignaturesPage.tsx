import { useEffect, useMemo, useState } from "react";
import { Download, Copy, Sparkles } from "lucide-react";

import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Button } from "@/components/ui/button";
import { DonorChip, DonorField, DonorFieldGrid, DonorSelect } from "../components/DonorForm";
import { DonorPanelPageLayout } from "../components/DonorPanelPageLayout";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { User } from "@/lib/types";

export function SignaturesPage() {
  const { token } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!token) {
      return;
    }

    setLoading(true);
    api
      .users(token)
      .then((data) => {
        setUsers(data.items);
        setSelectedUserId(data.items[0]?.id ?? "");
        setError(null);
      })
      .catch(() => setError("Não foi possível carregar colaboradores para assinatura."))
      .finally(() => setLoading(false));
  }, [token]);

  async function generatePreview() {
    if (!token || !selectedUserId) {
      return;
    }

    try {
      setGenerating(true);
      setPreview(await api.signatureGenerate(token, selectedUserId));
      setCopied(false);
      setError(null);
    } catch (err) {
      const detail = err instanceof Error ? err.message : "";
      setError(detail.includes("422") ? "O colaborador precisa ter e-mail para gerar assinatura." : "Não foi possível gerar o preview de assinatura.");
    } finally {
      setGenerating(false);
    }
  }

  async function copyPreview() {
    if (!preview) {
      return;
    }

    await navigator.clipboard.writeText(preview);
    setCopied(true);
  }

  async function downloadHtml() {
    if (!token || !selectedUserId) {
      return;
    }

    try {
      const html = await api.signatureDownloadHtml(token, selectedUserId);
      const blob = new Blob([html], { type: "text/html;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "assinatura-ens.html";
      link.click();
      URL.revokeObjectURL(url);
      setError(null);
    } catch {
      setError("Não foi possível baixar o HTML da assinatura.");
    }
  }

  const selectedUser = users.find((user) => user.id === selectedUserId);
  const stats = useMemo(
    () => [
      { label: "Colaboradores", value: users.length, detail: "Registros carregados para assinatura." },
      { label: "Selecionado", value: selectedUser ? selectedUser.name : "-", detail: selectedUser?.email ?? "Escolha um colaborador." },
      { label: "Preview", value: preview ? "Gerado" : "Pendente", detail: generating ? "Gerando com a API real." : copied ? "Copiado para a área de transferência." : "Aguardando ação." },
    ],
    [copied, generating, preview, selectedUser, users.length],
  );

  const userOptions = users.map((user) => ({
    value: user.id,
    label: user.name,
    description: user.email,
  }));

  return (
    <DonorPanelPageLayout
      eyebrow="Apoema Assinaturas"
      title="Assinaturas corporativas"
      description="Escolha o colaborador, gere o preview e copie ou baixe o HTML produzido pela API real."
      actions={
        <>
          <DonorChip>{generating ? "Gerando" : "Pronto"}</DonorChip>
          <Button className="rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300" type="button" onClick={() => void generatePreview()} disabled={!selectedUserId || generating}>
            <Sparkles className="h-4 w-4" />
            {generating ? "Gerando..." : "Gerar preview"}
          </Button>
        </>
      }
      stats={stats}
    >
      {error ? <Alert tone="danger">{error}</Alert> : null}
      {copied ? <Alert tone="success">HTML da assinatura copiado.</Alert> : null}
      {loading ? <LoadingBlock /> : null}

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
        <section className="rounded-[26px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_50px_-26px_rgba(0,0,0,0.8)]">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Colaborador</p>
              <h3 className="mt-2 text-lg font-semibold text-slate-50">Selecionar para gerar assinatura</h3>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">Use o usuário real da base. O preview é produzido pela API e mantém o fluxo de cópia/exportação.</p>
            </div>
            <DonorChip>{users.length} colaborador(es)</DonorChip>
          </div>

          <div className="mt-5 space-y-4">
            <DonorSelect
              label="Colaborador"
              value={selectedUserId}
              options={userOptions}
              placeholder="Selecione um colaborador"
              onChange={setSelectedUserId}
            />

            {selectedUser ? (
              <div className="rounded-[22px] border border-white/10 bg-slate-950/45 p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-50">{selectedUser.name}</p>
                    <p className="mt-1 break-words text-sm text-slate-300">{selectedUser.email}</p>
                    <p className="mt-1 break-words text-xs text-slate-500">
                      {selectedUser.department ?? "Sem departamento"} • {selectedUser.job_title ?? "Sem cargo"}
                    </p>
                  </div>
                  <DonorChip>{selectedUser.status}</DonorChip>
                </div>
              </div>
            ) : (
              <div className="rounded-[22px] border border-dashed border-white/15 bg-slate-950/35 p-4 text-sm text-slate-400">
                Selecione um colaborador para habilitar o preview.
              </div>
            )}

            <DonorFieldGrid className="grid-cols-1 sm:grid-cols-2">
              <DonorField label="Ações rápidas" hint="Copiar e baixar ficam disponíveis após a geração do preview.">
                <div className="flex flex-wrap gap-2">
                  <Button type="button" variant="outline" className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10" onClick={() => void copyPreview()} disabled={!preview}>
                    <Copy className="h-4 w-4" />
                    Copiar HTML
                  </Button>
                  <Button type="button" variant="outline" className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10" onClick={() => void downloadHtml()} disabled={!selectedUserId}>
                    <Download className="h-4 w-4" />
                    Baixar HTML
                  </Button>
                </div>
              </DonorField>
            </DonorFieldGrid>
          </div>
        </section>

        <section className="rounded-[26px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_50px_-26px_rgba(0,0,0,0.8)]">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Preview</p>
              <h3 className="mt-2 text-lg font-semibold text-slate-50">Assinatura gerada</h3>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">A visualização permanece honesta e usa o HTML bruto retornado pela API.</p>
            </div>
            <DonorChip>{preview ? "Gerado" : "Pendente"}</DonorChip>
          </div>

          <div className="mt-5 min-h-[420px] overflow-hidden rounded-[22px] border border-white/10 bg-slate-950/45">
            {preview ? (
              <iframe title="Preview de assinatura" srcDoc={preview} className="min-h-[420px] w-full min-w-0 border-0 bg-white" />
            ) : (
              <div className="grid min-h-[420px] place-items-center p-6 text-center">
                <div className="max-w-md space-y-3">
                  <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-200/70">Aguardando geração</p>
                  <p className="text-lg font-semibold text-slate-50">Selecione um colaborador e clique em Gerar preview.</p>
                  <p className="text-sm leading-6 text-slate-300">Quando o HTML for produzido, você poderá copiar ou baixar a assinatura.</p>
                </div>
              </div>
            )}
          </div>
        </section>
      </div>
    </DonorPanelPageLayout>
  );
}
