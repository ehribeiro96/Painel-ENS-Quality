import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { HermesStatusPill } from "@/components/brand/HermesStatusPill";
import { SentinelSectionHeader } from "@/components/brand/SentinelSectionHeader";
import { Alert, LoadingBlock } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { MacroTemplate } from "@/lib/types";

export function MacrosPage() {
  const { token } = useAuth();
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
  const autocompleteFields = new Set(["Nome", "Usuário Atual", "Usuário Anterior"]);
  const focusedValue = focusedField ? values[focusedField] ?? "" : "";

  const hintsQuery = useQuery({
    queryKey: ["macro-autocomplete", focusedField, focusedValue],
    enabled: Boolean(token && focusedField && autocompleteFields.has(focusedField)),
    queryFn: () => api.macroAutocomplete(token as string, focusedValue)
  });

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

  return (
    <>
      <SentinelSectionHeader
        chips={selected ? <HermesStatusPill state="Auditável">{selected.slug === "ativos-atualizar-inventario" ? "Macro pós-movimentação" : "Macro operativa"}</HermesStatusPill> : null}
        eyebrow="Macros ITIL"
        subtitle="Gere textos padronizados para chamados, movimentações e atendimento."
        title="Macros ITIL"
      />
      <div className="ops-panel compact-panel">
        <label className="wide-field">
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
      {templatesQuery.isError ? <Alert tone="danger">Não foi possível carregar macros.</Alert> : null}
      {templatesQuery.isLoading ? <LoadingBlock /> : null}
      {error ? <Alert tone="danger">{error}</Alert> : null}
      <div className="macro-layout">
        <section className="macro-list">
          {templates.length === 0 && !templatesQuery.isLoading ? <p className="muted">Nenhuma macro encontrada. Verifique o seed oficial do quality_macros_project.</p> : null}
          {templates.map((template) => (
            <button
              className={template.id === selected?.id ? "macro-item active" : "macro-item"}
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
        </section>
        <section className="macro-workbench">
          {selected ? (
            <>
              <h2>{selected.name}</h2>
              <p className="muted">{selected.description ?? selected.slug}</p>
              {selected.slug === "ativos-atualizar-inventario" ? <span className="badge attention">Usada em movimentações de ativos</span> : null}
              <p className="helper-text">Preencha os campos disponíveis. Campos não preenchidos aparecerão como pendentes.</p>
              <div className="form-grid">
                {selected.required_fields.map((field) => (
                  <label key={field}>
                    <span>{field} <strong aria-hidden>*</strong></span>
                    <input
                      className="input full"
                      list={autocompleteFields.has(field) ? "macro-collaborator-hints" : undefined}
                      value={values[field] ?? ""}
                      onBlur={() => setFocusedField((current) => (current === field ? null : current))}
                      onChange={(event) => setValues((current) => ({ ...current, [field]: event.target.value }))}
                      onFocus={() => setFocusedField(field)}
                    />
                  </label>
                ))}
              </div>
              <datalist id="macro-collaborator-hints">
                {(hintsQuery.data ?? []).map((hint) => <option key={hint.id} value={hint.label} />)}
              </datalist>
              <div className="modal-actions">
                <button className="button secondary" type="button" onClick={() => void generate(selected)}>Gerar preview</button>
                <button className="button" type="button" onClick={() => void copyRendered()} disabled={!rendered || !generationId}>Copiar macro</button>
              </div>
              {pendingFields.length > 0 ? (
                <Alert tone="danger">
                  Esta macro possui campos pendentes. Revise antes de copiar.
                  <span className="chip-row">
                    {pendingFields.map((field) => <span className="badge pending" key={field}>{field}</span>)}
                  </span>
                </Alert>
              ) : null}
              {copyStatus ? <Alert tone="success">{copyStatus}</Alert> : null}
              {rendered ? (
                <textarea className="textarea macro-preview" readOnly value={rendered} rows={12} />
              ) : (
                <div className="empty-preview">
                  Preencha os campos e clique em Gerar preview.
                </div>
              )}
            </>
          ) : (
            <p className="muted">Selecione uma macro para visualizar.</p>
          )}
        </section>
      </div>
    </>
  );
}
