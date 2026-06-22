import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Eye, History, Pencil, RotateCcw, SlidersHorizontal, Trash2 } from "lucide-react";
import { Base44ActionBar } from "@/components/base44/Base44ActionBar";
import { Base44AssetCard } from "@/components/base44/Base44AssetCard";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44MetricCard } from "@/components/base44/Base44MetricCard";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
import { DataTable } from "@/components/DataTable";
import { MoveAssetDialog } from "@/components/MoveAssetDialog";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatAssetStatus } from "@/lib/format";
import { canDeleteOperationalData, canWriteOperationalData } from "@/lib/permissions";
import { useDebouncedValue } from "@/lib/useDebouncedValue";
import { useLocalStorageState } from "@/lib/useLocalStorageState";
import type { Asset, AssetStatus, AssetType, Page } from "@/lib/types";

type AssetFilters = {
  search: string;
  status: string;
  assetType: string;
  location: string;
  availability: string;
  pageSize: number;
};

type AssetForm = {
  hostname: string;
  patrimony: string;
  serial: string;
  manufacturer: string;
  model: string;
  asset_type: AssetType;
  status: AssetStatus;
  location: string;
  operating_system: string;
  ip_address: string;
  notes: string;
};

const defaultFilters: AssetFilters = {
  search: "",
  status: "",
  assetType: "",
  location: "",
  availability: "",
  pageSize: 50
};

const defaultColumns = ["hostname", "patrimony", "current_user", "status", "location", "updated_at", "actions"];
const allColumns = [
  ["hostname", "Hostname"],
  ["patrimony", "Patrimônio"],
  ["serial", "Serial"],
  ["current_user", "Usuário atual"],
  ["status", "Status"],
  ["location", "Localidade"],
  ["asset_type", "Tipo"],
  ["manufacturer", "Fabricante"],
  ["model", "Modelo"],
  ["updated_at", "Última atualização"]
] as const;

const statusOptions: AssetStatus[] = ["IN_USE", "STOCK", "MAINTENANCE", "DEFECTIVE", "DISCARDED", "RESERVED", "CONFIG_PENDING"];
const typeOptions: AssetType[] = ["NOTEBOOK", "DESKTOP", "MONITOR", "DOCK", "MOBILE", "PRINTER", "PERIPHERAL", "OTHER"];
const emptyAssetForm: AssetForm = {
  hostname: "",
  patrimony: "",
  serial: "",
  manufacturer: "",
  model: "",
  asset_type: "OTHER",
  status: "STOCK",
  location: "",
  operating_system: "",
  ip_address: "",
  notes: ""
};

function formFromAsset(asset: Asset): AssetForm {
  return {
    hostname: asset.hostname ?? "",
    patrimony: asset.patrimony ?? "",
    serial: asset.serial ?? "",
    manufacturer: asset.manufacturer ?? "",
    model: asset.model ?? "",
    asset_type: asset.asset_type,
    status: asset.status,
    location: asset.location ?? "",
    operating_system: asset.operating_system ?? "",
    ip_address: asset.ip_address ?? "",
    notes: asset.notes ?? ""
  };
}

function payloadFromAssetForm(form: AssetForm) {
  return {
    hostname: form.hostname.trim() || null,
    patrimony: form.patrimony.trim() || null,
    serial: form.serial.trim() || null,
    manufacturer: form.manufacturer.trim() || null,
    model: form.model.trim() || null,
    asset_type: form.asset_type,
    status: form.status,
    location: form.location.trim() || null,
    operating_system: form.operating_system.trim() || null,
    ip_address: form.ip_address.trim() || null,
    notes: form.notes.trim() || null
  };
}

export function AssetsPage() {
  const { token, user: currentUser } = useAuth();
  const [urlParams] = useSearchParams();
  const queryClient = useQueryClient();
  const [filters, setFilters] = useLocalStorageState<AssetFilters>("itam.assets.filters", defaultFilters);
  const [visibleColumns, setVisibleColumns] = useLocalStorageState<string[]>("itam.assets.columns", defaultColumns);
  const [pageNumber, setPageNumber] = useState(1);
  const [sortBy, setSortBy] = useState("updated_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [showColumns, setShowColumns] = useState(false);
  const [movingAsset, setMovingAsset] = useState<Asset | null>(null);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [assetForm, setAssetForm] = useState<AssetForm>(emptyAssetForm);
  const [assetFormOpen, setAssetFormOpen] = useState(false);
  const [assetMessage, setAssetMessage] = useState<string | null>(null);
  const debouncedSearch = useDebouncedValue(filters.search, 350);
  const canWrite = canWriteOperationalData(currentUser?.role);
  const canDelete = canDeleteOperationalData(currentUser?.role);

  useEffect(() => {
    const nextStatus = urlParams.get("status");
    const nextAvailability = urlParams.get("availability");
    if (nextStatus || nextAvailability) {
      setFilters({
        ...filters,
        status: nextStatus ?? filters.status,
        availability: nextAvailability ?? filters.availability
      });
      setPageNumber(1);
    }
    // URL params are only used to seed operational shortcuts.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const queryString = useMemo(() => {
    const params = new URLSearchParams();
    params.set("page", String(pageNumber));
    params.set("page_size", String(filters.pageSize));
    params.set("sort_by", sortBy);
    params.set("sort_order", sortOrder);
    if (debouncedSearch.trim()) params.set("search", debouncedSearch.trim());
    if (filters.status) params.set("status", filters.status);
    if (filters.assetType) params.set("asset_type", filters.assetType);
    if (filters.location.trim()) params.set("location", filters.location.trim());
    if (filters.availability === "available") params.set("status", "STOCK");
    if (filters.availability === "assigned") params.set("status", "IN_USE");
    if (filters.availability === "unassigned") params.set("without_user", "true");
    return `?${params.toString()}`;
  }, [debouncedSearch, filters.assetType, filters.availability, filters.location, filters.pageSize, filters.status, pageNumber, sortBy, sortOrder]);

  const assetsQuery = useQuery({
    queryKey: ["assets", queryString],
    enabled: Boolean(token),
    queryFn: () => api.assets(token as string, queryString)
  });

  const usersQuery = useQuery({
    queryKey: ["users", "movement-select"],
    enabled: Boolean(token),
    queryFn: () => api.users(token as string, "?page_size=100")
  });

  const stockMutation = useMutation({
    mutationFn: (asset: Asset) =>
      api.moveAsset(token as string, asset.id, {
        new_user_id: null,
        new_status: "STOCK",
        new_location: asset.location,
        justification: "Envio rapido para estoque via tabela operacional.",
        notes: null
      }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["assets"] })
  });

  const saveAssetMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => {
      if (editingAsset) {
        return api.updateAsset(token as string, editingAsset.id, payload);
      }
      return api.createAsset(token as string, payload);
    },
    onSuccess: () => {
      setAssetMessage(editingAsset ? "Ativo atualizado." : "Ativo criado.");
      setEditingAsset(null);
      setAssetForm(emptyAssetForm);
      setAssetFormOpen(false);
      void queryClient.invalidateQueries({ queryKey: ["assets"] });
    }
  });

  const deleteAssetMutation = useMutation({
    mutationFn: (asset: Asset) => api.deleteAsset(token as string, asset.id),
    onSuccess: () => {
      setAssetMessage("Ativo desativado com seguranca. Historico preservado.");
      void queryClient.invalidateQueries({ queryKey: ["assets"] });
    }
  });

  function updateFilter<K extends keyof AssetFilters>(key: K, value: AssetFilters[K]) {
    setPageNumber(1);
    setFilters({ ...filters, [key]: value });
  }

  function clearFilters() {
    setPageNumber(1);
    setFilters(defaultFilters);
  }

  function toggleSort(key: string) {
    if (sortBy === key) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key);
      setSortOrder("asc");
    }
  }

  function toggleColumn(key: string) {
    const next = visibleColumns.includes(key)
      ? visibleColumns.filter((column) => column !== key)
      : [...visibleColumns, key];
    setVisibleColumns(next.length ? next : defaultColumns);
  }

  function openCreateAsset() {
    setEditingAsset(null);
    setAssetForm(emptyAssetForm);
    setAssetFormOpen(true);
    setAssetMessage(null);
  }

  function openEditAsset(asset: Asset) {
    setEditingAsset(asset);
    setAssetForm(formFromAsset(asset));
    setAssetFormOpen(true);
    setAssetMessage(null);
  }

  function submitAssetForm(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = payloadFromAssetForm(assetForm);
    if (!payload.hostname && !payload.patrimony && !payload.serial) {
      setAssetMessage("Informe ao menos hostname, patrimonio ou serial para identificar o ativo.");
      return;
    }
    saveAssetMutation.mutate(payload);
  }

  function deactivateAsset(asset: Asset) {
    const confirmed = window.confirm("Este ativo possui historico operacional e sera desativado, nao removido definitivamente. Continuar?");
    if (!confirmed) return;
    deleteAssetMutation.mutate(asset);
  }

  const page = assetsQuery.data as Page<Asset> | undefined;
  const pageItems = page?.items ?? [];
  const totalPages = page ? Math.max(1, Math.ceil(page.total / page.page_size)) : 1;
  const summary = useMemo(() => {
    const total = page?.total ?? 0;
    const assigned = pageItems.filter((asset) => asset.status === "IN_USE").length;
    const stock = pageItems.filter((asset) => asset.status === "STOCK").length;
    const incomplete = pageItems.filter((asset) => isIncomplete(asset)).length;
    return { total, assigned, stock, incomplete };
  }, [page?.total, pageItems]);

  function isIncomplete(asset: Asset) {
    return !asset.hostname || asset.hostname === "-" || !asset.patrimony || asset.patrimony === "-";
  }

  const columns = useMemo(() => {
    const definitions = {
      hostname: {
        key: "hostname",
        label: "Tag",
        sortable: true,
        render: (asset: Asset) => (
          <span className="cell-stack">
            <Link to={`/assets/${asset.id}`}>{asset.hostname && asset.hostname !== "-" ? asset.hostname : "Sem tag"}</Link>
            {isIncomplete(asset) ? <span className="badge warning">Cadastro incompleto</span> : null}
          </span>
        )
      },
      patrimony: { key: "patrimony", label: "Patrimônio", sortable: true, render: (asset: Asset) => asset.patrimony && asset.patrimony !== "-" ? asset.patrimony : <span className="muted">Não informado</span> },
      serial: { key: "serial", label: "Serial", sortable: true },
      current_user: { key: "current_user", label: "Colaborador", render: (asset: Asset) => asset.current_user?.name ?? <span className="badge neutral">Sem usuário</span> },
      status: {
        key: "status",
        label: "Status",
        sortable: true,
        render: (asset: Asset) => <Base44StatusBadge status={asset.status}>{formatAssetStatus(asset.status)}</Base44StatusBadge>
      },
      location: { key: "location", label: "Unidade", sortable: true },
      asset_type: { key: "asset_type", label: "Tipo" },
      manufacturer: { key: "manufacturer", label: "Marca" },
      model: { key: "model", label: "Modelo" },
      updated_at: { key: "updated_at", label: "Última movimentação", sortable: true, render: (asset: Asset) => new Date(asset.updated_at).toLocaleString("pt-BR") }
    };
    return allColumns
      .map(([key]) => definitions[key])
      .filter((column) => visibleColumns.includes(column.key));
  }, [visibleColumns]);

  return (
    <div className="base44-asset-page">
      <Base44PageHeader
        eyebrow="Inventário técnico"
        title="Ativos"
        description="Busca operacional com filtros, visão salva e ações diretas por linha."
        breadcrumbs={[
          <Link key="dashboard" to="/">Dashboard</Link>,
          <span key="sep-1">/</span>,
          <span key="assets">Ativos</span>
        ]}
        actions={
          <>
            <button className="button secondary" type="button" onClick={() => setShowColumns(!showColumns)}>
              <SlidersHorizontal size={16} aria-hidden />
              Colunas
            </button>
            {canWrite ? <button className="button" type="button" onClick={openCreateAsset}>+ Novo ativo</button> : null}
          </>
        }
      />

      <section className="grid metrics base44-asset-metrics" aria-label="Resumo do inventário filtrado">
        <Base44MetricCard title="Total encontrado" value={summary.total} description="Quantidade total retornada pelos filtros atuais." icon={Archive} />
        <Base44MetricCard title="Em estoque" value={summary.stock} description="Ativos prontos para nova movimentação nesta página." icon={RotateCcw} />
        <Base44MetricCard title="Em uso" value={summary.assigned} description="Ativos vinculados a usuários nesta página." icon={Eye} />
        <Base44MetricCard title="Cadastro incompleto" value={summary.incomplete} description="Ativos que ainda pedem hostname, patrimônio ou serial." icon={History} />
      </section>

      <Base44Surface className="base44-asset-permission" as="section">
        <div>
          <p className="base44-eyebrow">Permissões</p>
          <h2>{canWrite ? "Escrita operacional ativa" : "Modo consulta"}</h2>
          <p>
            {canWrite
              ? "Seu perfil pode criar, editar e movimentar ativos. A desativação continua restrita ao administrador."
              : "Seu perfil pode navegar, filtrar e abrir detalhes, mas as ações de cadastro e desativação ficam ocultas."}
          </p>
        </div>
        <div className="base44-chip-row">
          <Base44StatusBadge status={canWrite ? "auditavel" : "leitura"}>{canWrite ? "Escrita habilitada" : "Consulta"}</Base44StatusBadge>
          <Base44StatusBadge status={canDelete ? "auditavel" : "leitura"}>{canDelete ? "Desativação ativa" : "Sem exclusão"}</Base44StatusBadge>
        </div>
      </Base44Surface>

      {assetFormOpen && canWrite ? (
        <Base44Surface className="base44-asset-form" as="form" onSubmit={submitAssetForm}>
          <div className="base44-form-header">
            <div>
              <p className="base44-eyebrow">Cadastro operacional</p>
              <h2>{editingAsset ? "Editar ativo" : "Novo ativo"}</h2>
              <p>Edicao cadastral. Troca de usuario, status ou local operacional deve usar Movimentar.</p>
            </div>
            <button className="button secondary" type="button" onClick={() => setAssetFormOpen(false)}>Fechar</button>
          </div>
          <div className="form-grid base44-asset-form-grid">
            <label>Hostname<input className="input full" value={assetForm.hostname} onChange={(event) => setAssetForm({ ...assetForm, hostname: event.target.value })} /></label>
            <label>Patrimônio<input className="input full" value={assetForm.patrimony} onChange={(event) => setAssetForm({ ...assetForm, patrimony: event.target.value })} /></label>
            <label>Serial<input className="input full" value={assetForm.serial} onChange={(event) => setAssetForm({ ...assetForm, serial: event.target.value })} /></label>
            <label>Tipo
              <select className="select full" value={assetForm.asset_type} onChange={(event) => setAssetForm({ ...assetForm, asset_type: event.target.value as AssetType })}>
                {typeOptions.map((type) => <option key={type} value={type}>{type}</option>)}
              </select>
            </label>
            <label>Fabricante<input className="input full" value={assetForm.manufacturer} onChange={(event) => setAssetForm({ ...assetForm, manufacturer: event.target.value })} /></label>
            <label>Modelo<input className="input full" value={assetForm.model} onChange={(event) => setAssetForm({ ...assetForm, model: event.target.value })} /></label>
            <label>Status cadastral
              <select className="select full" value={assetForm.status} onChange={(event) => setAssetForm({ ...assetForm, status: event.target.value as AssetStatus })}>
                {statusOptions.map((status) => <option key={status} value={status}>{formatAssetStatus(status)}</option>)}
              </select>
            </label>
            <label>Localização<input className="input full" value={assetForm.location} onChange={(event) => setAssetForm({ ...assetForm, location: event.target.value })} /></label>
            <label>Sistema operacional<input className="input full" value={assetForm.operating_system} onChange={(event) => setAssetForm({ ...assetForm, operating_system: event.target.value })} /></label>
            <label>IP<input className="input full" value={assetForm.ip_address} onChange={(event) => setAssetForm({ ...assetForm, ip_address: event.target.value })} /></label>
            <label className="wide-field">Observações<textarea className="input full" value={assetForm.notes} onChange={(event) => setAssetForm({ ...assetForm, notes: event.target.value })} /></label>
          </div>
          <button className="button" type="submit" disabled={saveAssetMutation.isPending}>{saveAssetMutation.isPending ? "Salvando..." : editingAsset ? "Salvar ativo" : "Criar ativo"}</button>
        </Base44Surface>
      ) : null}

      <Base44ActionBar
        eyebrow="Filtros operacionais"
        title="Recorte do inventário"
        description="Busca, status, tipo, localidade e quantidade por página continuam usando os dados reais da API."
        actions={
          <button className="button secondary" type="button" onClick={clearFilters}>
            <RotateCcw size={16} aria-hidden />
            Limpar
          </button>
        }
      >
        <div className="base44-asset-filters-grid">
          <label className="wide-field">
            Busca unificada
            <input
              className="input full"
              placeholder="Hostname, patrimônio, serial, usuário, e-mail ou localidade"
              value={filters.search}
              onChange={(event) => updateFilter("search", event.target.value)}
            />
          </label>
          <label>
            Status
            <select className="select full" value={filters.status} onChange={(event) => updateFilter("status", event.target.value)}>
              <option value="">Todos</option>
              {statusOptions.map((status) => <option key={status} value={status}>{formatAssetStatus(status)}</option>)}
            </select>
          </label>
          <label>
            Tipo
            <select className="select full" value={filters.assetType} onChange={(event) => updateFilter("assetType", event.target.value)}>
              <option value="">Todos</option>
              {typeOptions.map((type) => <option key={type} value={type}>{type}</option>)}
            </select>
          </label>
          <label>
            Localidade
            <input className="input full" value={filters.location} onChange={(event) => updateFilter("location", event.target.value)} />
          </label>
          <label>
            Disponibilidade
            <select className="select full" value={filters.availability} onChange={(event) => updateFilter("availability", event.target.value)}>
              <option value="">Todas</option>
              <option value="available">Disponíveis</option>
              <option value="assigned">Em uso</option>
            </select>
          </label>
          <label>
            Linhas
            <select className="select full" value={filters.pageSize} onChange={(event) => updateFilter("pageSize", Number(event.target.value))}>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
          </label>
        </div>
      </Base44ActionBar>

      {showColumns ? (
        <Base44Surface className="base44-asset-columns-panel" as="section">
          <div className="base44-form-header">
            <div>
              <p className="base44-eyebrow">Colunas</p>
              <h2>Visibilidade da tabela</h2>
              <p>As colunas apenas ajustam a leitura visual; os dados e a ordenação continuam sendo reais.</p>
            </div>
          </div>
          <div className="base44-chip-row">
            {allColumns.map(([key, label]) => (
              <label className="check-pill" key={key}>
                <input type="checkbox" checked={visibleColumns.includes(key)} onChange={() => toggleColumn(key)} />
                {label}
              </label>
            ))}
          </div>
        </Base44Surface>
      ) : null}

      {stockMutation.isError ? <Alert tone="danger">Não foi possível enviar o ativo para estoque.</Alert> : null}
      {saveAssetMutation.isError ? <Alert tone="danger">Não foi possível salvar o ativo. Verifique identidade unica, tipo e campos obrigatorios.</Alert> : null}
      {deleteAssetMutation.isError ? <Alert tone="danger">Não foi possível desativar o ativo.</Alert> : null}
      {assetMessage ? <Alert tone={assetMessage.includes("Informe") ? "danger" : "success"}>{assetMessage}</Alert> : null}
      {assetsQuery.isError ? <Alert tone="danger">Não foi possível carregar os ativos.</Alert> : null}
      {assetsQuery.isLoading ? <LoadingBlock label="Carregando ativos com filtros server-side..." /> : null}

      <Base44Surface className="base44-asset-result-shell" as="section">
        <div className="base44-asset-result-summary">
          <strong>{page?.total ?? 0}</strong> ativos encontrados
          {assetsQuery.isFetching && !assetsQuery.isLoading ? <span>Atualizando...</span> : null}
        </div>

        {pageItems.length > 0 ? (
          <>
            <Base44AssetCard
              asset={pageItems[0]}
              actions={
                <div className="row-action-group base44-asset-card-actions-inline">
                  <Link className="mini-button" to={`/assets/${pageItems[0].id}`} title="Ver detalhes" aria-label="Ver detalhes do ativo"><Eye size={15} aria-hidden /></Link>
                  {canWrite ? <button className="mini-button" type="button" title="Editar ativo" aria-label="Editar ativo" onClick={() => openEditAsset(pageItems[0])}><Pencil size={15} aria-hidden /></button> : null}
                  <button className="mini-button text-action" type="button" title="Movimentar ativo" aria-label="Movimentar ativo" onClick={() => setMovingAsset(pageItems[0])}>Movimentar</button>
                  <button className="mini-button" type="button" title="Enviar para estoque" disabled={stockMutation.isPending} onClick={() => stockMutation.mutate(pageItems[0])}>
                    <Archive size={15} aria-hidden />
                  </button>
                  {canDelete ? <button className="mini-button danger" type="button" title="Desativar ativo" aria-label="Desativar ativo" disabled={deleteAssetMutation.isPending} onClick={() => deactivateAsset(pageItems[0])}><Trash2 size={15} aria-hidden /></button> : null}
                  <Link className="mini-button" to={`/assets/${pageItems[0].id}#history`} title="Histórico" aria-label="Ver histórico do ativo"><History size={15} aria-hidden /></Link>
                </div>
              }
            />

            <div className="asset-table-shell base44-asset-table-shell">
              <DataTable
                items={pageItems}
                columns={columns}
                sortBy={sortBy}
                sortOrder={sortOrder}
                onSort={toggleSort}
                emptyTitle="Nenhum ativo encontrado."
                emptyDescription={canWrite
                  ? "Ajuste os filtros para encontrar um ativo existente ou crie o primeiro registro operacional."
                  : "Ajuste os filtros para ampliar a busca ou remova o recorte atual."}
                emptyActions={canWrite ? <button className="button" type="button" onClick={openCreateAsset}>+ Novo ativo</button> : <button className="button secondary" type="button" onClick={clearFilters}>Limpar filtros</button>}
                rowActions={(asset) => (
                  <div className="row-action-group">
                    <Link className="mini-button" to={`/assets/${asset.id}`} title="Ver detalhes" aria-label="Ver detalhes do ativo"><Eye size={15} aria-hidden /></Link>
                    {canWrite ? <button className="mini-button" type="button" title="Editar ativo" aria-label="Editar ativo" onClick={() => openEditAsset(asset)}><Pencil size={15} aria-hidden /></button> : null}
                    <button className="mini-button text-action" type="button" title="Movimentar ativo" aria-label="Movimentar ativo" onClick={() => setMovingAsset(asset)}>Movimentar</button>
                    <button className="mini-button" type="button" title="Enviar para estoque" disabled={stockMutation.isPending} onClick={() => stockMutation.mutate(asset)}>
                      <Archive size={15} aria-hidden />
                    </button>
                    {canDelete ? <button className="mini-button danger" type="button" title="Desativar ativo" aria-label="Desativar ativo" disabled={deleteAssetMutation.isPending} onClick={() => deactivateAsset(asset)}><Trash2 size={15} aria-hidden /></button> : null}
                    <Link className="mini-button" to={`/assets/${asset.id}#history`} title="Histórico" aria-label="Ver histórico do ativo"><History size={15} aria-hidden /></Link>
                  </div>
                )}
              />

              <nav className="pagination" aria-label="Paginação de ativos">
                <button className="button secondary" type="button" disabled={pageNumber <= 1} onClick={() => setPageNumber(pageNumber - 1)}>Anterior</button>
                <span>Página {pageNumber} de {totalPages}</span>
                <button className="button secondary" type="button" disabled={pageNumber >= totalPages} onClick={() => setPageNumber(pageNumber + 1)}>Próxima</button>
              </nav>
            </div>
          </>
        ) : (
          <Base44EmptyState
            title="Nenhum ativo encontrado"
            description={canWrite
              ? "Ajuste os filtros para encontrar um ativo existente ou crie o primeiro registro operacional."
              : "Ajuste os filtros para ampliar a busca ou remova o recorte atual."}
            action={canWrite ? <button className="button" type="button" onClick={openCreateAsset}>+ Novo ativo</button> : <button className="button secondary" type="button" onClick={clearFilters}>Limpar filtros</button>}
          />
        )}
      </Base44Surface>

      <MoveAssetDialog
        asset={movingAsset}
        token={token ?? ""}
        users={usersQuery.data}
        onClose={() => setMovingAsset(null)}
        onMoved={() => {
          void queryClient.invalidateQueries({ queryKey: ["assets"] });
        }}
      />
    </div>
  );
}
