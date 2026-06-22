import { useEffect, useState } from "react";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Base44CopyBlock } from "@/components/base44/Base44CopyBlock";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44OperationalGrid } from "@/components/base44/Base44OperationalGrid";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
import { Base44UserCard } from "@/components/base44/Base44UserCard";
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
  const summaryItems = [
    { title: "Colaboradores", value: users.length, description: "Registros carregados para assinatura.", accent: loading ? "Carregando" : "API real" },
    { title: "Selecionado", value: selectedUser ? selectedUser.name : "-", description: "Colaborador usado no preview atual.", accent: selectedUser ? selectedUser.role : "Nenhum" },
    { title: "Preview", value: preview ? "Gerado" : "Pendente", description: "HTML produzido pela API de assinatura.", accent: generating ? "Gerando" : copied ? "Copiado" : "Pronto" }
  ];

  const selectedHtml = preview;

  return (
    <div className="base44-operation-page">
      <Base44PageHeader
        eyebrow="Assinaturas corporativas"
        title="Assinaturas Corporativas"
        description="Gere assinaturas de email padronizadas com a mesma base visual Base44 e os mesmos contratos reais de colaboradores."
        actions={
          <>
            <Base44StatusBadge status={generating ? "warning" : "auditavel"}>{generating ? "Gerando" : "Pronto"}</Base44StatusBadge>
            <button className="button" type="button" onClick={() => void generatePreview()} disabled={!selectedUserId || generating}>
              {generating ? "Gerando..." : "Gerar"}
            </button>
          </>
        }
      />

      <Base44OperationalGrid
        title="Resumo da assinatura"
        description="Os cartões abaixo refletem o estado atual da seleção e da geração do preview."
        columns={3}
        items={summaryItems}
      />

      {error ? <Alert tone="danger">{error}</Alert> : null}
      {copied ? <Alert tone="success">HTML da assinatura copiado.</Alert> : null}
      {loading ? <LoadingBlock /> : null}

      <section className="base44-operation-columns">
        <Base44Surface className="base44-operation-panel" as="section">
          <div className="base44-operation-panel-head">
            <div>
              <p className="base44-eyebrow">Dados</p>
              <h2>Colaborador selecionado</h2>
              <p className="base44-operation-panel-description">Escolha o colaborador e o preview seguirá a fonte real da API.</p>
            </div>
            <Base44StatusBadge status="auditavel">{users.length} colaborador(es)</Base44StatusBadge>
          </div>

          <label className="base44-operation-select">
            <span>Colaborador</span>
            <select className="select wide" value={selectedUserId} onChange={(event) => setSelectedUserId(event.target.value)}>
              <option value="">Selecione um colaborador</option>
              {users.map((user) => <option key={user.id} value={user.id}>{user.name} - {user.email}</option>)}
            </select>
          </label>

          {selectedUser ? (
            <Base44UserCard
              user={selectedUser}
              actions={<Base44StatusBadge status={selectedUser.status === "ACTIVE" ? "success" : selectedUser.status === "INACTIVE" ? "leitura" : "warning"}>{selectedUser.status}</Base44StatusBadge>}
            />
          ) : null}

          <div className="base44-operation-actions">
            <button className="button secondary" type="button" onClick={() => void copyPreview()} disabled={!preview}>Copiar HTML</button>
            <button className="button secondary" type="button" onClick={() => void downloadHtml()} disabled={!selectedUserId}>Baixar HTML</button>
            <a className="button secondary" href="/assinaturas/" target="_blank" rel="noreferrer">Abrir legado</a>
          </div>
        </Base44Surface>

        <Base44Surface className="base44-operation-panel" as="section">
          <div className="base44-operation-panel-head">
            <div>
              <p className="base44-eyebrow">Preview</p>
              <h2>Assinatura gerada</h2>
              <p className="base44-operation-panel-description">A visualização continua sendo um iframe sobre o HTML gerado pela API real.</p>
            </div>
            <Base44StatusBadge status={preview ? "success" : "warning"}>{preview ? "Gerada" : "Pendente"}</Base44StatusBadge>
          </div>
          {preview ? (
            <div className="base44-operation-preview-shell">
              <iframe title="Preview de assinatura" srcDoc={preview} />
              <Base44CopyBlock
                title="HTML gerado"
                description="O HTML pode ser copiado ou baixado sem alterar a lógica de assinatura."
                value={selectedHtml}
                onCopy={() => void copyPreview()}
                copyLabel="Copiar HTML"
              />
            </div>
          ) : (
            <Base44EmptyState title="Selecione um colaborador" description="Depois de gerar o preview, a assinatura aparecerá nesta área com a identidade Base44." />
          )}
        </Base44Surface>
      </section>
    </div>
  );
}
