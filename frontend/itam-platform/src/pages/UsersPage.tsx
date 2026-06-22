import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { DataTable } from "@/components/DataTable";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44FilterPanel } from "@/components/base44/Base44FilterPanel";
import { Base44OperationalGrid } from "@/components/base44/Base44OperationalGrid";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
import { Base44UserCard } from "@/components/base44/Base44UserCard";
import { Base44UserRoleBadge } from "@/components/base44/Base44UserRoleBadge";
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

  async function submitForm(event: FormEvent<HTMLFormElement>) {
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

  const spotlight = userRows.slice(0, 3);

  return (
    <div className="base44-user-page">
      <Base44PageHeader
        eyebrow="Colaboradores"
        title="Colaboradores / Usuários"
        description="Cadastro canônico usado por ativos, assinaturas, auditoria e vínculos operacionais, com a identidade visual Base44 aplicada sobre os mesmos contratos reais."
        actions={
          <>
            <Base44StatusBadge status={canWrite ? "auditavel" : "leitura"}>{canWrite ? "Escrita ativa" : "Modo consulta"}</Base44StatusBadge>
            <Base44StatusBadge status={canDelete ? "auditavel" : "leitura"}>{canDelete ? "Exclusão ativa" : "Sem exclusão"}</Base44StatusBadge>
          </>
        }
      />

      <Base44OperationalGrid
        title="Resumo de colaboradores"
        description="Os indicadores abaixo vêm da página e da consulta real corrente."
        columns={4}
        items={[
          { title: "Total encontrado", value: totalUsers, description: "Colaboradores retornados pela consulta atual.", accent: hasSearch ? "Busca ativa" : "Sem busca" },
          { title: "Ativos", value: summary.active, description: "Registros liberados para uso operacional.", accent: "Operação" },
          { title: "Administradores", value: summary.admins, description: "Perfis com settings sensíveis e exclusões.", accent: "RBAC" },
          { title: "Legados", value: summary.legacy, description: "Registros originados do ENS legado.", accent: "Histórico" }
        ]}
      />

      {!canWrite ? (
        <Alert tone="info">Seu perfil permite visualizar colaboradores, mas não criar ou editar registros.</Alert>
      ) : null}

      <Base44FilterPanel
        eyebrow="Busca e filtros"
        title="Localizar colaborador"
        description="A busca textual continua ligada ao parâmetro real enviado para a API."
        actions={<Base44StatusBadge status={hasSearch ? "warning" : "auditavel"}>{hasSearch ? `Busca: ${trimmedSearch}` : "Sem busca ativa"}</Base44StatusBadge>}
      >
        <div className="b44-filter-grid">
          <label>
            Busca
            <input
              className="input full"
              placeholder="Buscar por nome, identificador do e-mail, e-mail ou departamento..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </label>
          <div className="base44-user-filter-tags">
            <span className="filter-chip muted">Unidade: em breve</span>
            <span className="filter-chip muted">Situação: em breve</span>
            <span className="filter-chip muted">RBAC real preservado</span>
          </div>
        </div>
      </Base44FilterPanel>

      <section className="base44-user-workspace">
        <Base44Surface className="base44-user-form-shell" as="section">
          {canWrite && isFormOpen ? (
            <form className="base44-user-form" onSubmit={(event) => void submitForm(event)}>
              <div className="base44-user-form-head">
                <div>
                  <p className="base44-eyebrow">Cadastro operacional</p>
                  <h2>{formTitle}</h2>
                  <p className="base44-user-form-description">{formDescription}</p>
                </div>
                <div className="base44-chip-row">
                  <Base44StatusBadge status="auditavel">{editingUser ? "Edição" : "Criação manual"}</Base44StatusBadge>
                  <button className="button secondary" type="button" onClick={closeForm} disabled={saving}>Cancelar</button>
                </div>
              </div>
              <div className="base44-user-form-grid">
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
              <div className="base44-user-form-actions">
                <button className="button" type="submit" disabled={saving}>{saving ? "Salvando..." : editingUser ? "Salvar alterações" : "Criar colaborador"}</button>
                <button className="button secondary" type="button" onClick={closeForm} disabled={saving}>Cancelar</button>
              </div>
            </form>
          ) : canWrite ? (
            <Base44EmptyState
              title="Cadastro recolhido"
              description="Use “Novo colaborador” para abrir o formulário. Para alterar um registro existente, escolha “Editar” na tabela."
              action={<button className="button" type="button" onClick={openCreate}>+ Novo colaborador</button>}
            />
          ) : (
            <Base44EmptyState
              title="Modo consulta"
              description="Seu perfil pode visualizar colaboradores, mas não pode criar ou editar registros."
            />
          )}
        </Base44Surface>

        <Base44Surface className="base44-user-spotlight-shell" as="section">
          <div className="base44-user-spotlight-head">
            <div>
              <p className="base44-eyebrow">Destaques carregados</p>
              <h2>Primeiros resultados</h2>
              <p className="base44-user-spotlight-description">Uma visão rápida dos registros já carregados na consulta atual.</p>
            </div>
            <Base44StatusBadge status="auditavel">{summary.current} item(ns)</Base44StatusBadge>
          </div>
          {spotlight.length ? (
            <div className="base44-user-spotlight-grid">
              {spotlight.map((user) => (
                <Base44UserCard
                  key={user.id}
                  user={user}
                  actions={
                    <div className="base44-chip-row">
                      <Base44UserRoleBadge role={user.role} />
                      <Link className="button secondary" to={`/users/${user.id}`}>Abrir detalhe</Link>
                    </div>
                  }
                />
              ))}
            </div>
          ) : (
            <Base44EmptyState title="Sem destaques" description="Quando a consulta retornar usuários, alguns cards aparecerão aqui para inspeção rápida." />
          )}
        </Base44Surface>
      </section>

      {success ? <Alert tone="success"><strong>{success}</strong></Alert> : null}
      {error ? <Alert tone="danger"><strong>{error}</strong></Alert> : null}
      {loading ? <LoadingBlock label="Carregando colaboradores..." /> : null}

      <Base44Surface className="base44-user-table-shell" as="section">
        <div className="base44-user-table-head">
          <div>
            <h2 className="card-title">Lista de colaboradores</h2>
            <p className="card-description">
              {hasSearch ? "Resultado filtrado pela busca textual." : "Todos os colaboradores retornados pela API atual."}
            </p>
          </div>
          <Base44StatusBadge status={hasSearch ? "warning" : "auditavel"}>{totalUsers} colaborador(es)</Base44StatusBadge>
        </div>
        <div className="base44-user-table-body">
          {userRows.length === 0 ? (
            <Base44EmptyState
              title={hasSearch ? "Nenhum colaborador corresponde à busca." : "Sem colaboradores cadastrados."}
              description={hasSearch ? "Tente remover parte do termo pesquisado ou limpar o campo de busca." : canWrite ? "Crie o primeiro colaborador para liberar vínculos, auditoria e cadastros operacionais." : "Sua sessão está em modo consulta. Quando houver dados, eles aparecerão aqui."}
              action={hasSearch ? <button className="button secondary" type="button" onClick={() => setSearch("")}>Limpar busca</button> : canWrite ? <button className="button" type="button" onClick={openCreate}>+ Novo colaborador</button> : null}
            />
          ) : (
            <div className="base44-user-table-wrap">
              <Base44Surface className="base44-user-table-surface" as="div">
                <div className="base44-user-table-caption">Tabela operacional preservada com os contratos reais de usuários.</div>
                <div className="base44-user-table-inner">
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
                      { key: "name", label: "Nome", render: (user: User) => <Link to={`/users/${user.id}`}>{user.name}</Link> },
                      { key: "login", label: "Identificador", render: (user: User) => <span className="cell-stack"><strong>{user.email.split("@")[0] ?? "-"}</strong><small>derivado do e-mail</small></span> },
                      { key: "email", label: "E-mail", className: "email-cell", render: (user: User) => <span title={user.email}>{user.email}</span> },
                      { key: "business_unit", label: "Unidade", render: (user: User) => user.business_unit ?? "-" },
                      { key: "department", label: "Dept.", render: (user: User) => user.department ?? "-" },
                      { key: "source", label: "Fonte", render: (user: User) => <Base44StatusBadge status="leitura">{sourceLabel(user.source)}</Base44StatusBadge> },
                      { key: "role", label: "Perfil", render: (user: User) => <Base44UserRoleBadge role={user.role} /> },
                      {
                        key: "status",
                        label: "Situação",
                        render: (user: User) => (
                          <Base44StatusBadge status={user.status === "ACTIVE" ? "success" : user.status === "INACTIVE" ? "leitura" : "warning"} title={statusDescription(user.status)}>
                            {statusLabel(user.status)}
                          </Base44StatusBadge>
                        )
                      }
                    ]}
                    rowActions={(user: User) => (
                      <div className="row-action-group users-row-actions">
                        {canWrite ? <button className="mini-button text-action" type="button" onClick={() => openEdit(user)}>Editar</button> : null}
                        {canDelete ? <button className="mini-button danger text-action" type="button" disabled={saving} onClick={() => void deactivateUser(user)}>Desativar</button> : null}
                      </div>
                    )}
                  />
                </div>
              </Base44Surface>
            </div>
          )}
        </div>
      </Base44Surface>
    </div>
  );
}
