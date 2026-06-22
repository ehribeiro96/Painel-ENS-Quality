import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { DataTable } from "@/components/DataTable";
import { AlertBlock, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { canDeleteOperationalData, canWriteOperationalData } from "@/lib/permissions";
import type { Page, Role, User, UserStatus } from "@/lib/types";

type UserForm = {
  name: string;
  email: string;
  job_title: string;
  department: string;
  business_unit: string;
  manager_name: string;
  phone: string;
  status: UserStatus;
};

const emptyForm: UserForm = {
  name: "",
  email: "",
  job_title: "",
  department: "",
  business_unit: "",
  manager_name: "",
  phone: "",
  status: "ACTIVE"
};

function sourceLabel(source: string | null | undefined) {
  if (source === "legacy_ens_db") return "Legacy ENS DB";
  if (source === "manual") return "Manual";
  if (source === "entra_id" || source === "graph") return "Futuro AD/Entra";
  return "Não informado";
}

function statusLabel(status: UserStatus) {
  return status === "ACTIVE" ? "Ativo" : status === "INACTIVE" ? "Inativo" : "Afastado";
}

function statusDescription(status: UserStatus) {
  if (status === "ACTIVE") return "Pode participar de vínculos e operação.";
  if (status === "INACTIVE") return "Mantido para histórico, auditoria e vínculos antigos.";
  return "Usuário temporariamente fora da operação.";
}

function roleLabel(role: Role) {
  const labels: Record<Role, string> = {
    ADMIN: "Admin",
    TECHNICIAN: "Técnico",
    VIEWER: "Consulta",
    MANAGER: "Gestor"
  };
  return labels[role] ?? role;
}

function roleBadgeTone(role: Role) {
  if (role === "ADMIN") return "danger";
  if (role === "TECHNICIAN") return "info";
  if (role === "MANAGER") return "warning";
  return "neutral";
}

function formFromUser(user: User): UserForm {
  return {
    name: user.name,
    email: user.email,
    job_title: user.job_title ?? "",
    department: user.department ?? "",
    business_unit: user.business_unit ?? "",
    manager_name: user.manager_name ?? "",
    phone: user.phone ?? "",
    status: user.status
  };
}

function payloadFromForm(form: UserForm) {
  return {
    name: form.name.trim(),
    email: form.email.trim(),
    job_title: form.job_title.trim() || null,
    department: form.department.trim() || null,
    business_unit: form.business_unit.trim() || null,
    manager_name: form.manager_name.trim() || null,
    phone: form.phone.trim() || null,
    status: form.status,
    source: "manual"
  };
}

export function UsersPage() {
  const { token, user: currentUser } = useAuth();
  const [page, setPage] = useState<Page<User> | null>(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [form, setForm] = useState<UserForm>(emptyForm);

  const canWrite = canWriteOperationalData(currentUser?.role);
  const canDelete = canDeleteOperationalData(currentUser?.role);
  const trimmedSearch = search.trim();

  const query = useMemo(() => {
    return trimmedSearch ? `&search=${encodeURIComponent(trimmedSearch)}` : "";
  }, [trimmedSearch]);

  async function loadUsers() {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.users(token, query);
      setPage(data);
      setError(null);
    } catch {
      setError("Não foi possível carregar os colaboradores. Atualize a página e verifique se sua sessão ainda está ativa.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, query]);

  function openCreate() {
    setEditingUser(null);
    setForm(emptyForm);
    setIsFormOpen(true);
    setError(null);
    setSuccess(null);
  }

  function closeForm() {
    setEditingUser(null);
    setForm(emptyForm);
    setIsFormOpen(false);
  }

  function openEdit(user: User) {
    setEditingUser(user);
    setForm(formFromUser(user));
    setIsFormOpen(true);
    setError(null);
    setSuccess(null);
  }

  async function submitForm(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !canWrite) return;
    setSaving(true);
    try {
      const payload = payloadFromForm(form);
      if (editingUser) {
        await api.updateUser(token, editingUser.id, payload);
        setSuccess("Colaborador atualizado.");
      } else {
        await api.createUser(token, payload);
        setSuccess("Colaborador criado.");
      }
      closeForm();
      await loadUsers();
    } catch {
      setError("Não foi possível salvar. Verifique nome, e-mail único e campos obrigatórios.");
    } finally {
      setSaving(false);
    }
  }

  async function deactivateUser(user: User) {
    if (!token || !canDelete) return;
    const confirmed = window.confirm("Desativar este colaborador? Histórico, auditoria e vínculos existentes serão preservados.");
    if (!confirmed) return;
    setSaving(true);
    try {
      await api.deleteUser(token, user.id);
      setSuccess("Colaborador desativado com segurança.");
      await loadUsers();
    } catch {
      setError("Não foi possível desativar o colaborador.");
    } finally {
      setSaving(false);
    }
  }

  const totalUsers = page?.total ?? 0;
  const userRows = page?.items ?? [];
  const hasSearch = Boolean(trimmedSearch);
  const emptyMessage = hasSearch
    ? `Nenhum colaborador encontrado para “${trimmedSearch}”. Ajuste a busca e tente novamente.`
    : canWrite
      ? "Nenhum colaborador cadastrado ainda. Use Novo colaborador para criar o primeiro registro."
      : "Nenhum colaborador cadastrado ainda.";
  const formTitle = editingUser ? "Editar colaborador" : "Novo colaborador";
  const formDescription = editingUser
    ? "Atualize somente dados cadastrais e status operacional. Role, senha e flags administrativas não são editadas aqui."
    : "Cadastre um colaborador manual sem alterar permissões, autenticação ou vínculos existentes.";
  const summary = useMemo(() => {
    const active = userRows.filter((user) => user.status === "ACTIVE").length;
    const admins = userRows.filter((user) => user.role === "ADMIN").length;
    const legacy = userRows.filter((user) => user.source === "legacy_ens_db").length;
    const manual = userRows.filter((user) => user.source === "manual").length;
    return { active, admins, legacy, manual, current: userRows.length };
  }, [userRows]);

  return (
    <>
      <header className="page-title page-header users-page-header">
        <div>
          <span className="badge info">Colaboradores</span>
          <h1>Colaboradores / Usuários</h1>
          <p>Cadastro canônico usado por ativos, assinaturas, auditoria e vínculos operacionais.</p>
        </div>
        <div className="page-actions">
          {canWrite ? <button className="button" type="button" onClick={openCreate}>+ Novo colaborador</button> : null}
        </div>
      </header>

      <section className="grid metrics page-metrics users-metrics" aria-label="Resumo de colaboradores">
        <article className="card metric-card">
          <span className="metric-label">Total encontrado</span>
          <strong className="metric-value">{totalUsers}</strong>
          <p className="metric-description">Colaboradores retornados pela consulta atual.</p>
        </article>
        <article className="card metric-card">
          <span className="metric-label">Ativos</span>
          <strong className="metric-value">{summary.active}</strong>
          <p className="metric-description">Registros liberados para uso operacional.</p>
        </article>
        <article className="card metric-card">
          <span className="metric-label">Administradores</span>
          <strong className="metric-value">{summary.admins}</strong>
          <p className="metric-description">Perfis com exclusão e settings sensíveis.</p>
        </article>
        <article className="card metric-card">
          <span className="metric-label">Nesta página</span>
          <strong className="metric-value">{summary.current}</strong>
          <p className="metric-description">Linhas visíveis na listagem atual.</p>
        </article>
      </section>

      {!canWrite ? (
        <AlertBlock tone="info">
          <strong>Modo consulta</strong>
          <p>Seu perfil permite visualizar colaboradores, mas não criar ou editar registros.</p>
        </AlertBlock>
      ) : null}

      <section className="filter-bar users-toolbar" aria-label="Busca de colaboradores">
        <label className="wide-field">
          Busca
          <input
            className="input full"
            placeholder="Buscar por nome, identificador do e-mail, e-mail ou departamento..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <span className={`filter-chip ${hasSearch ? "active" : ""}`}>{hasSearch ? `Busca ativa: ${trimmedSearch}` : "Sem busca ativa"}</span>
        <span className="filter-chip muted">Unidade: em breve</span>
        <span className="filter-chip muted">Situação: em breve</span>
      </section>

      {canWrite && isFormOpen ? (
        <form className="form-panel users-form-card" onSubmit={(event) => void submitForm(event)}>
          <div className="form-panel-header">
            <div>
              <span className="badge neutral">{editingUser ? "Edição" : "Criação manual"}</span>
              <h2>{formTitle}</h2>
              <p>{formDescription}</p>
            </div>
            <button className="button secondary" type="button" onClick={closeForm} disabled={saving}>Cancelar</button>
          </div>
          <div className="form-grid users-form-grid">
            <label>Nome<input className="input full" required minLength={2} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label>
            <label>E-mail<input className="input full" required type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label>
            <label>Cargo<input className="input full" value={form.job_title} onChange={(event) => setForm({ ...form, job_title: event.target.value })} /></label>
            <label>Departamento<input className="input full" value={form.department} onChange={(event) => setForm({ ...form, department: event.target.value })} /></label>
            <label>Unidade<input className="input full" value={form.business_unit} onChange={(event) => setForm({ ...form, business_unit: event.target.value })} /></label>
            <label>Gestor<input className="input full" value={form.manager_name} onChange={(event) => setForm({ ...form, manager_name: event.target.value })} /></label>
            <label>Telefone<input className="input full" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} /></label>
            <label>Status
              <select className="select full" value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as UserStatus })}>
                <option value="ACTIVE">Ativo</option>
                <option value="INACTIVE">Inativo</option>
                <option value="ON_LEAVE">Afastado</option>
              </select>
              <small>{statusDescription(form.status)}</small>
            </label>
          </div>
          <div className="form-panel-actions">
            <button className="button" type="submit" disabled={saving}>{saving ? "Salvando..." : editingUser ? "Salvar alterações" : "Criar colaborador"}</button>
            <button className="button secondary" type="button" onClick={closeForm} disabled={saving}>Cancelar</button>
          </div>
        </form>
      ) : canWrite ? (
        <div className="permission-note users-form-card">
          <strong>Cadastro recolhido</strong>
          <p>Use “Novo colaborador” para abrir o formulário. Para alterar um registro existente, escolha “Editar” na tabela.</p>
        </div>
      ) : null}

      {success ? <AlertBlock tone="success"><strong>{success}</strong></AlertBlock> : null}
      {error ? <AlertBlock tone="danger"><strong>{error}</strong></AlertBlock> : null}
      {loading ? <LoadingBlock label="Carregando colaboradores..." /> : null}

      <section className="card users-table-card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Lista de colaboradores</h2>
            <p className="card-description">
              {hasSearch ? "Resultado filtrado pela busca textual." : "Todos os colaboradores retornados pela API atual."}
            </p>
          </div>
          <span className={`badge ${hasSearch ? "info" : "neutral"}`}>{totalUsers} colaborador(es)</span>
        </div>
        <DataTable
          items={userRows}
          emptyMessage={emptyMessage}
          emptyTitle={hasSearch ? "Nenhum colaborador corresponde à busca." : "Sem colaboradores cadastrados."}
          emptyDescription={hasSearch
            ? "Tente remover parte do termo pesquisado ou limpar o campo de busca."
            : canWrite
              ? "Crie o primeiro colaborador para liberar vínculos, auditoria e cadastros operacionais."
              : "Sua sessão está em modo consulta. Quando houver dados, eles aparecerão aqui."}
          emptyActions={hasSearch
            ? <button className="button secondary" type="button" onClick={() => setSearch("")}>Limpar busca</button>
            : canWrite
              ? <button className="button" type="button" onClick={openCreate}>+ Novo colaborador</button>
              : null}
          columns={[
            { key: "name", label: "Nome", render: (user) => <Link to={`/users/${user.id}`}>{user.name}</Link> },
            { key: "login", label: "Identificador", render: (user) => <span className="cell-stack"><strong>{user.email.split("@")[0] ?? "-"}</strong><small>derivado do e-mail</small></span> },
            { key: "email", label: "E-mail", className: "email-cell", render: (user) => <span title={user.email}>{user.email}</span> },
            { key: "business_unit", label: "Unidade", render: (user) => user.business_unit ?? "-" },
            { key: "department", label: "Dept.", render: (user) => user.department ?? "-" },
            { key: "source", label: "Fonte", render: (user) => <span className="badge neutral">{sourceLabel(user.source)}</span> },
            { key: "role", label: "Perfil", render: (user) => <span className={`badge ${roleBadgeTone(user.role)}`}>{roleLabel(user.role)}</span> },
            {
              key: "status",
              label: "Situação",
              render: (user) => (
                <span className={`badge ${user.status === "ACTIVE" ? "success" : user.status === "INACTIVE" ? "neutral" : "warning"}`} title={statusDescription(user.status)}>
                  {statusLabel(user.status)}
                </span>
              )
            }
          ]}
          rowActions={(user) => (
            <div className="row-action-group users-row-actions">
              {canWrite ? <button className="mini-button text-action" type="button" onClick={() => openEdit(user)}>Editar</button> : null}
              {canDelete ? <button className="mini-button danger text-action" type="button" disabled={saving} onClick={() => void deactivateUser(user)}>Desativar</button> : null}
            </div>
          )}
        />
      </section>
    </>
  );
}
