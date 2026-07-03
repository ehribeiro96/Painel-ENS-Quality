import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Pencil, Plus, Search, Trash2, Users } from "lucide-react";

import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DonorPanelPageLayout } from "../components/DonorPanelPageLayout";
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
  status: "ACTIVE",
};

function sourceLabel(source: string | null | undefined) {
  if (source === "legacy_ens_db") return "Legacy ENS DB";
  if (source === "manual") return "Manual";
  if (source === "entra_id" || source === "graph") return "Entra/Graph";
  return "Não informado";
}

function statusLabel(status: UserStatus) {
  return status === "ACTIVE" ? "Ativo" : status === "INACTIVE" ? "Inativo" : "Afastado";
}

function roleLabel(role: Role) {
  const labels: Record<Role, string> = {
    ADMIN: "Admin",
    TECHNICIAN: "Técnico",
    VIEWER: "Consulta",
    MANAGER: "Gestor",
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
    status: user.status,
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
    source: "manual",
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
    setError(null);
    setSuccess(null);
  }

  function openEdit(userToEdit: User) {
    setEditingUser(userToEdit);
    setForm(formFromUser(userToEdit));
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
      setEditingUser(null);
      setForm(emptyForm);
      await loadUsers();
    } catch {
      setError("Não foi possível salvar. Verifique nome, e-mail único e campos obrigatórios.");
    } finally {
      setSaving(false);
    }
  }

  async function deactivateUser(userToDelete: User) {
    if (!token || !canDelete) return;
    const confirmed = window.confirm("Desativar este colaborador? Histórico, auditoria e vínculos existentes serão preservados.");
    if (!confirmed) return;
    setSaving(true);
    try {
      await api.deleteUser(token, userToDelete.id);
      setSuccess("Colaborador desativado com segurança.");
      await loadUsers();
    } catch {
      setError("Não foi possível desativar o colaborador.");
    } finally {
      setSaving(false);
    }
  }

  const userRows = page?.items ?? [];
  const totalUsers = page?.total ?? 0;
  const hasSearch = Boolean(trimmedSearch);
  const summary = useMemo(() => {
    const active = userRows.filter((user) => user.status === "ACTIVE").length;
    const admins = userRows.filter((user) => user.role === "ADMIN").length;
    const legacy = userRows.filter((user) => user.source === "legacy_ens_db").length;
    return { active, admins, legacy };
  }, [userRows]);

  return (
    <DonorPanelPageLayout
      eyebrow="Usuários"
      title="Cadastro operacional"
      description="Colaboradores usados por ativos, assinaturas, auditoria e vínculos operacionais, em uma interface limpa e donor-first."
      actions={
        <>
          <Button asChild variant="outline" className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10">
            <Link to="/apoema/signatures">Gerar assinatura</Link>
          </Button>
          <Button type="button" className="rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300" onClick={openCreate} disabled={!canWrite}>
            <Plus className="h-4 w-4" />
            Novo colaborador
          </Button>
        </>
      }
      stats={[
        { label: "Total encontrado", value: totalUsers, detail: "Colaboradores retornados pela consulta atual." },
        { label: "Ativos", value: summary.active, detail: "Registros liberados para uso operacional." },
        { label: "Administradores", value: summary.admins, detail: "Perfis com settings sensíveis." },
        { label: "Legados", value: summary.legacy, detail: "Registros originados do ENS legado." },
      ]}
    >
      {!canWrite ? <Alert tone="info">Seu perfil permite visualizar colaboradores, mas não criar ou editar registros.</Alert> : null}
      {error ? <Alert tone="danger">{error}</Alert> : null}
      {success ? <Alert tone="success">{success}</Alert> : null}
      {loading ? <LoadingBlock label="Carregando colaboradores..." /> : null}

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(0,0.95fr)]">
        <article className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Busca</p>
              <h3 className="mt-1 text-lg font-semibold text-slate-50">Localizar colaborador</h3>
            </div>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
              {hasSearch ? `Busca: ${trimmedSearch}` : "Sem busca ativa"}
            </span>
          </div>

          <label className="flex items-center gap-2 rounded-2xl border border-white/10 bg-slate-950/50 px-3 py-3 text-slate-300">
            <Search className="h-4 w-4 shrink-0 text-slate-500" />
            <input
              className="w-full bg-transparent text-sm outline-none placeholder:text-slate-500"
              placeholder="Buscar por nome, identificador do e-mail, e-mail ou departamento..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </label>

          <div className="mt-4 overflow-hidden rounded-[24px] border border-white/10">
            <div className="overflow-x-auto">
              <table className="min-w-full border-collapse text-left text-sm">
                <thead className="bg-slate-950/70 text-slate-300">
                  <tr>
                    {["Nome", "Perfil", "Status", "Departamento", "Unidade", "Origem"].map((header) => (
                      <th key={header} className="whitespace-nowrap px-4 py-3 text-xs font-semibold uppercase tracking-[0.18em]">
                        {header}
                      </th>
                    ))}
                    <th className="px-4 py-3 text-xs font-semibold uppercase tracking-[0.18em]">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10 bg-slate-950/35">
                  {userRows.length === 0 ? (
                    <tr>
                      <td className="px-4 py-8" colSpan={7}>
                        <div className="rounded-[22px] border border-dashed border-white/15 bg-slate-950/35 p-5 text-slate-300">
                          Nenhum colaborador encontrado.
                        </div>
                      </td>
                    </tr>
                  ) : (
                    userRows.map((userItem) => (
                      <tr key={userItem.id} className="align-top">
                        <td className="px-4 py-4">
                          <div className="space-y-1">
                            <button type="button" className="font-medium text-slate-50 hover:underline" onClick={() => openEdit(userItem)}>
                              {userItem.name}
                            </button>
                            <p className="text-xs text-slate-400">{userItem.email}</p>
                          </div>
                        </td>
                        <td className="px-4 py-4 text-slate-300">{roleLabel(userItem.role)}</td>
                        <td className="px-4 py-4 text-slate-300">{statusLabel(userItem.status)}</td>
                        <td className="px-4 py-4 text-slate-300">{userItem.department ?? "-"}</td>
                        <td className="px-4 py-4 text-slate-300">{userItem.business_unit ?? "-"}</td>
                        <td className="px-4 py-4 text-slate-300">{sourceLabel(userItem.source)}</td>
                        <td className="px-4 py-4">
                          <div className="flex flex-wrap gap-2">
                            <Button
                              type="button"
                              variant="outline"
                              className="h-9 rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10"
                              onClick={() => openEdit(userItem)}
                            >
                              <Pencil className="h-4 w-4" />
                              Editar
                            </Button>
                            <Button
                              type="button"
                              variant="outline"
                              className="h-9 rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-rose-500/10 hover:text-rose-100"
                              onClick={() => void deactivateUser(userItem)}
                              disabled={!canDelete}
                            >
                              <Trash2 className="h-4 w-4" />
                              Excluir
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </article>

        <article className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.32em] text-cyan-200/70">Cadastro</p>
              <h3 className="mt-1 text-lg font-semibold text-slate-50">{editingUser ? "Editar colaborador" : "Novo colaborador"}</h3>
            </div>
            <Users className="h-4 w-4 text-cyan-100" />
          </div>

          <form className="space-y-4" onSubmit={submitForm}>
            <div className="grid gap-3">
              <label className="space-y-2 text-sm text-slate-300">
                Nome
                <Input
                  className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500"
                  value={form.name}
                  onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                />
              </label>
              <label className="space-y-2 text-sm text-slate-300">
                E-mail
                <Input
                  className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500"
                  value={form.email}
                  onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                />
              </label>
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="space-y-2 text-sm text-slate-300">
                  Cargo
                  <Input
                    className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500"
                    value={form.job_title}
                    onChange={(event) => setForm((current) => ({ ...current, job_title: event.target.value }))}
                  />
                </label>
                <label className="space-y-2 text-sm text-slate-300">
                  Departamento
                  <Input
                    className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500"
                    value={form.department}
                    onChange={(event) => setForm((current) => ({ ...current, department: event.target.value }))}
                  />
                </label>
                <label className="space-y-2 text-sm text-slate-300">
                  Unidade
                  <Input
                    className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500"
                    value={form.business_unit}
                    onChange={(event) => setForm((current) => ({ ...current, business_unit: event.target.value }))}
                  />
                </label>
                <label className="space-y-2 text-sm text-slate-300">
                  Gestor
                  <Input
                    className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500"
                    value={form.manager_name}
                    onChange={(event) => setForm((current) => ({ ...current, manager_name: event.target.value }))}
                  />
                </label>
                <label className="space-y-2 text-sm text-slate-300 sm:col-span-2">
                  Telefone
                  <Input
                    className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500"
                    value={form.phone}
                    onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))}
                  />
                </label>
              </div>
              <label className="space-y-2 text-sm text-slate-300">
                Status
                <select
                  className="w-full rounded-2xl border border-white/10 bg-white/5 px-3 py-3 text-sm text-slate-50 outline-none"
                  value={form.status}
                  onChange={(event) => setForm((current) => ({ ...current, status: event.target.value as UserStatus }))}
                >
                  <option value="ACTIVE">Ativo</option>
                  <option value="INACTIVE">Inativo</option>
                  <option value="ON_LEAVE">Afastado</option>
                </select>
              </label>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button type="submit" className="rounded-2xl bg-cyan-400 text-slate-950 hover:bg-cyan-300" disabled={!canWrite || saving}>
                {editingUser ? "Salvar alterações" : "Criar colaborador"}
              </Button>
              <Button
                type="button"
                variant="outline"
                className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10"
                onClick={() => {
                  setEditingUser(null);
                  setForm(emptyForm);
                }}
              >
                Limpar
              </Button>
            </div>
          </form>
        </article>
      </section>
    </DonorPanelPageLayout>
  );
}
