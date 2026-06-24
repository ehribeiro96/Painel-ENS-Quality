import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Search, Sparkles, TextCursorInput } from "lucide-react";

import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { Base44EmptyState } from "@/components/base44/Base44EmptyState";
import { Base44FilterPanel } from "@/components/base44/Base44FilterPanel";
import { Base44MacroPanel } from "@/components/base44/Base44MacroPanel";
import { Base44MacroPreview } from "@/components/base44/Base44MacroPreview";
import { Base44OperationalGrid } from "@/components/base44/Base44OperationalGrid";
import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { MacroTemplate } from "@/lib/types";

function normalizeFieldLabel(value: string) {
  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function isAutocompleteField(value: string) {
  const normalized = normalizeFieldLabel(value);
  return normalized.includes("nome") || normalized.includes("usuario") || normalized.includes("colaborador");
}

function formatStepLabel(template: MacroTemplate | null) {
  if (!template) return "Selecione uma macro";
  return template.slug === "ativos-atualizar-inventario" ? "Macro pós-movimentação" : "Macro operativa";
}

const ALLOWED_ROLES = new Set(["ADMIN", "TECHNICIAN"]);

export function MacrosPage() {
  const { token, user } = useAuth();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [rendered, setRendered] = useState("");
  const [generationId, setGenerationId] = useState<string | null>(null);
  const [pendingFields, setPendingFields] = useState<string[]>([]);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const templatesQuery = useQuery({
    queryKey: ["macro-templates", search, category],
    enabled: Boolean(token),
    queryFn: () => {
      const params = new URLSearchParams();
      if (search.trim()) params.set("search", search.trim());
      if (category.trim()) params.set("category", category.trim());
      const query = params.toString();
      return api.macroTemplates(token as string, query ? `?${query}` : "");
    }
  });

  const templates = templatesQuery.data ?? [];
  const selected = templates.find((template) => template.id === selectedId) ?? templates[0] ?? null;
  const categories = useMemo(() => Array.from(new Set(templates.map((template) => template.category))).sort(), [templates]);
  const focusedValue = focusedField ? values[focusedField] ?? "" : "";
  const activeAutocompleteField = focusedField && isAutocompleteField(focusedField) ? focusedField : null;

  const hintsQuery = useQuery({
    queryKey: ["macro-autocomplete", focusedField, focusedValue],
    enabled: Boolean(token && activeAutocompleteField),
    queryFn: () => api.macroAutocomplete(token as string, focusedValue)
  });

  const autocompleteHints = activeAutocompleteField ? (hintsQuery.data ?? []).slice(0, 8) : [];

  function readPendingFields(inputValues: Record<string, unknown>) {
    const metadata = inputValues._metadata;
    if (metadata && typeof metadata === "object" && "pending_fields" in metadata && Array.isArray(metadata.pending_fields)) {
      return metadata.pending_fields.filter((field): field is string => typeof field === "string");
    }
    return [];
  }

  async function generate(template: MacroTemplate) {
    setError(null);
    try {
      const response = await api.macroGenerate(token as string, {
        template_id: template.id,
        values
      });
      setRendered(response.rendered_text);
      setGenerationId(response.id);
      setPendingFields(readPendingFields(response.input_values));
      setCopyStatus(null);
    } catch {
      setGenerationId(null);
      setPendingFields([]);
      setError("Preencha os campos obrigatorios antes de renderizar a macro.");
    }
  }

  async function copyRendered() {
    if (!rendered || !generationId) return;
    await navigator.clipboard.writeText(rendered);
    await api.macroMarkCopied(token as string, generationId);
    setCopyStatus("Macro copiada.");
  }

  function applyHint(field: string, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
    setFocusedField(field);
    setCopyStatus(null);
  }

  if (user && !ALLOWED_ROLES.has(user.role)) {
    return <main className="screen-center">Acesso nao autorizado.</main>;
  }

  const summaryItems = [
    {
      title: "Macros encontradas",
      value: templates.length,
      description: "Resultados da consulta atual.",
      icon: Search,
      accent: search.trim() ? "Busca ativa" : "Sem filtro"
    },
    {
      title: "Categorias",
      value: categories.length,
      description: "Agrupamentos disponíveis no seed real.",
      icon: Sparkles,
      accent: category.trim() ? category : "Todas"
    },
    {
      title: "Campos obrigatórios",
      value: selected?.required_fields.length ?? 0,
      description: "Campos exigidos pela macro selecionada.",
      icon: TextCursorInput,
      accent: selected ? formatStepLabel(selected) : "Selecione uma macro"
    },
    {
      title: "Pendências",
      value: pendingFields.length,
      description: "Campos ainda pendentes no render atual.",
      icon: ArrowRight,
      accent: generationId ? `Geração ${generationId.slice(0, 8)}` : "Sem geração"
    }
  ];

  return (
    <div className="base44-macro-page">
      <Base44PageHeader
        eyebrow="Macros ITIL"
        title="Apoema Macros ITIL"
        description="Geração, preview e cópia continuam ligados à API real de macros, com uma camada visual Apoema para organização e hierarquia."
        actions={
          <>
            <Base44StatusBadge status={selected ? "auditavel" : "leitura"}>{formatStepLabel(selected)}</Base44StatusBadge>
            <Base44StatusBadge status={generationId ? "success" : "warning"}>{generationId ? "Geração ativa" : "Sem geração"}</Base44StatusBadge>
          </>
        }
      />
      <Base44OperationalGrid
        title="Resumo operacional"
        description="Os números abaixo vêm da consulta real de templates e do estado atual do render."
        columns={4}
        items={summaryItems}
      />

      <Base44FilterPanel
        eyebrow="Busca e filtro"
        title="Localizar macro"
        description="Filtre por nome, categoria ou slug antes de abrir a macro desejada."
        actions={<Base44StatusBadge status={templatesQuery.isLoading ? "warning" : "auditavel"}>{templatesQuery.isLoading ? "Carregando" : "API real"}</Base44StatusBadge>}
      >
        <div className="b44-filter-grid">
          <label>
            Busca
            <input className="input full" placeholder="Buscar macro por nome, categoria ou slug" value={search} onChange={(event) => setSearch(event.target.value)} />
          </label>
          <label>
            Categoria
            <select className="select full" value={category} onChange={(event) => setCategory(event.target.value)}>
              <option value="">Todas</option>
              {categories.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
        </div>
      </Base44FilterPanel>

      {templatesQuery.isError ? <Alert tone="danger">Não foi possível carregar macros.</Alert> : null}
      {templatesQuery.isLoading ? <LoadingBlock /> : null}
      {error ? <Alert tone="danger">{error}</Alert> : null}

      <section className="base44-macro-workspace">
        <Base44Surface className="base44-macro-list-shell" as="aside">
          <div className="base44-macro-list-head">
            <div>
              <p className="base44-eyebrow">Lista de macros</p>
              <h2>Templates disponíveis</h2>
              <p className="base44-macro-list-description">Selecione um template para abrir o editor de valores e o preview real.</p>
            </div>
            <Base44StatusBadge status="auditavel">{templates.length} item(ns)</Base44StatusBadge>
          </div>
          <div className="base44-macro-list">
            {templates.length === 0 && !templatesQuery.isLoading ? (
              <Base44EmptyState
                title="Nenhuma macro encontrada"
                description="Verifique o seed oficial do quality_macros_project ou refine a busca e a categoria."
              />
            ) : null}
            {templates.map((template) => (
              <button
                className={template.id === selected?.id ? "base44-macro-item is-selected" : "base44-macro-item"}
                key={template.id}
                type="button"
                onClick={() => {
                  setSelectedId(template.id);
                  setRendered("");
                  setGenerationId(null);
                  setPendingFields([]);
                  setCopyStatus(null);
                  setValues({});
                }}
              >
                <strong>{template.name}</strong>
                <span className="badge soft">{template.category}</span>
                {template.slug === "ativos-atualizar-inventario" ? <small>Usada em movimentações de ativos</small> : null}
              </button>
            ))}
          </div>
        </Base44Surface>

        <Base44MacroPanel
          eyebrow="Editor de macro"
          title={selected?.name ?? "Selecione uma macro"}
          description={selected ? selected.description ?? selected.slug : "Abra um template para editar os valores e gerar o conteúdo real."}
          status={selected ? formatStepLabel(selected) : "Nenhuma seleção"}
          actions={selected ? <Base44StatusBadge status={selected.slug === "ativos-atualizar-inventario" ? "warning" : "auditavel"}>{selected.slug}</Base44StatusBadge> : null}
        >
          {selected ? (
            <>
              <p className="base44-macro-panel-helper">Preencha os campos disponíveis. Campos não preenchidos aparecerão como pendentes no preview e na auditoria da geração.</p>
              <div className="base44-macro-field-grid">
                {selected.required_fields.map((field) => (
                  <label className="base44-macro-field" key={field}>
                    <span>{field} <strong aria-hidden>*</strong></span>
                    <div className="base44-macro-field-stack">
                      <input
                        className="input full"
                        autoComplete="off"
                        value={values[field] ?? ""}
                        onBlur={() => setFocusedField((current) => (current === field ? null : current))}
                        onChange={(event) => setValues((current) => ({ ...current, [field]: event.target.value }))}
                        onFocus={() => setFocusedField(field)}
                      />
                      {activeAutocompleteField === field ? (
                        <div className="base44-macro-autocomplete-panel" aria-label={`Sugestões para ${field}`}>
                          {hintsQuery.isFetching ? <span className="base44-macro-autocomplete-empty">Buscando sugestões...</span> : null}
                          {!hintsQuery.isFetching && autocompleteHints.length === 0 ? (
                            <span className="base44-macro-autocomplete-empty">Sem sugestões para este campo.</span>
                          ) : null}
                          {autocompleteHints.map((hint) => (
                            <button
                              className="base44-macro-autocomplete-item"
                              key={hint.id}
                              type="button"
                              onMouseDown={(event) => event.preventDefault()}
                              onClick={() => applyHint(field, hint.label)}
                            >
                              <strong>{hint.label}</strong>
                              <span>{hint.source.replaceAll("_", " ")}</span>
                            </button>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  </label>
                ))}
              </div>
              <Base44MacroPreview
                rendered={rendered}
                generationId={generationId}
                pendingFields={pendingFields}
                copyStatus={copyStatus}
                onGenerate={() => void generate(selected)}
                onCopy={() => void copyRendered()}
                footer={
                  <div className="base44-chip-row">
                    {pendingFields.length > 0 ? <Base44StatusBadge status="danger">{pendingFields.length} pendente(s)</Base44StatusBadge> : <Base44StatusBadge status="success">Campos completos</Base44StatusBadge>}
                    {selected.slug === "ativos-atualizar-inventario" ? <Base44StatusBadge status="warning">Macro pós-movimentação</Base44StatusBadge> : <Base44StatusBadge status="auditavel">Macro operativa</Base44StatusBadge>}
                  </div>
                }
              />
            </>
          ) : (
            <Base44EmptyState title="Selecione uma macro" description="A lista à esquerda mostra os templates reais e o editor abre ao escolher um item." />
          )}
        </Base44MacroPanel>
      </section>
    </div>
  );
}
