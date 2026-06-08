import { useEffect, useState } from "react";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
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

  return (
    <>
      <div className="page-title">
        <div>
          <h1>Assinaturas corporativas</h1>
          <p>Geração com dados canônicos do colaborador no PostgreSQL.</p>
        </div>
        <button className="button" type="button" onClick={() => void generatePreview()} disabled={!selectedUserId || generating}>
          {generating ? "Gerando..." : "Gerar"}
        </button>
      </div>
      {error ? <Alert tone="danger">{error}</Alert> : null}
      {copied ? <Alert tone="success">HTML da assinatura copiado.</Alert> : null}
      {loading ? <LoadingBlock /> : null}
      <div className="toolbar">
        <select className="select wide" value={selectedUserId} onChange={(event) => setSelectedUserId(event.target.value)}>
          <option value="">Selecione um colaborador</option>
          {users.map((user) => <option key={user.id} value={user.id}>{user.name} - {user.email}</option>)}
        </select>
        <button className="button secondary" type="button" onClick={() => void copyPreview()} disabled={!preview}>Copiar HTML</button>
        <button className="button secondary" type="button" onClick={() => void downloadHtml()} disabled={!selectedUserId}>Baixar HTML</button>
        <a className="button secondary" href="/assinaturas/" target="_blank" rel="noreferrer">Abrir legado</a>
      </div>
      {selectedUser ? (
        <section className="card">
          <h2>Dados usados na assinatura</h2>
          <p>{selectedUser.name} · {selectedUser.email}</p>
          <p>{selectedUser.job_title || "Cargo não informado"} · {selectedUser.department || "Departamento não informado"}</p>
        </section>
      ) : null}
      <section className="card signature-preview">
        {preview ? (
          <iframe title="Preview de assinatura" srcDoc={preview} />
        ) : (
          <div className="empty-state">
            Selecione um colaborador e clique em Gerar para visualizar a assinatura.
          </div>
        )}
      </section>
    </>
  );
}
