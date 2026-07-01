import { FileSliders, Layers3, Tags, WandSparkles } from "lucide-react";
import { useMemo } from "react";
import { StatusPill } from "./StatusPill";
import type { DesignerFormOptions, DesignerGenerationMode, DesignerTemplate } from "../types";

export type DesignerSelection = {
  template_id: string;
  canal: string;
  kv: string;
  modo_geracao: DesignerGenerationMode;
};

type Props = {
  templates: DesignerTemplate[];
  formOptions: DesignerFormOptions | null;
  value: DesignerSelection;
  onChange: (next: DesignerSelection) => void;
  loading?: boolean;
  error?: string | null;
};

export function DesignerTemplateSelector({ templates, formOptions, value, onChange, loading = false, error = null }: Props) {
  const selectedTemplate = useMemo(() => templates.find((template) => template.template_id === value.template_id) ?? null, [templates, value.template_id]);
  const allowedModes = selectedTemplate?.mode_options.length ? selectedTemplate.mode_options : formOptions?.modes ?? [];

  function updateTemplate(templateId: string) {
    const template = templates.find((item) => item.template_id === templateId) ?? null;
    const nextModes = template?.mode_options.length ? template.mode_options : formOptions?.modes ?? [];
    const nextMode = nextModes.includes(value.modo_geracao) ? value.modo_geracao : nextModes[0] ?? value.modo_geracao;
    onChange({
      template_id: templateId,
      canal: template?.canal || formOptions?.channels[0] || value.canal,
      kv: template?.kv || formOptions?.kvs[0] || value.kv,
      modo_geracao: nextMode,
    });
  }

  function updateMode(mode: DesignerGenerationMode) {
    const nextModes = selectedTemplate?.mode_options.length ? selectedTemplate.mode_options : formOptions?.modes ?? [];
    onChange({
      ...value,
      modo_geracao: nextModes.includes(mode) ? mode : nextModes[0] ?? mode,
    });
  }

  return (
    <section className="apoema-designer-selector">
      <div className="apoema-section-head">
        <div>
          <StatusPill tone="info">
            <FileSliders size={14} />
            Templates
          </StatusPill>
          <h3>Escopo do job</h3>
          <p>Selecione um template allowlisted e ajuste canal, KV e modo conforme o contrato do backend.</p>
        </div>
        <span>{loading ? "Carregando catálogo" : `${templates.length} template(s)`}</span>
      </div>

      {error ? (
        <div className="apoema-warning is-warning">
          <div>
            <strong>Catálogo indisponível</strong>
            <p>{error}</p>
          </div>
        </div>
      ) : null}

      <div className="apoema-designer-selector-grid">
        <label className="apoema-field">
          Template
          <select value={value.template_id} onChange={(event) => updateTemplate(event.target.value)} disabled={loading || templates.length === 0}>
            {templates.length === 0 ? <option value="">Sem templates</option> : null}
            {templates.map((template) => (
              <option key={template.template_id} value={template.template_id}>
                {template.label}
              </option>
            ))}
          </select>
        </label>

        <label className="apoema-field">
          Canal
          <select
            value={value.canal}
            onChange={(event) => onChange({ ...value, canal: event.target.value })}
            disabled={loading || (formOptions?.channels.length ?? 0) === 0}
          >
            {(formOptions?.channels ?? []).map((channel) => (
              <option key={channel} value={channel}>
                {channel}
              </option>
            ))}
          </select>
        </label>

        <label className="apoema-field">
          KV
          <select value={value.kv} onChange={(event) => onChange({ ...value, kv: event.target.value })} disabled={loading || (formOptions?.kvs.length ?? 0) === 0}>
            {(formOptions?.kvs ?? []).map((kv) => (
              <option key={kv} value={kv}>
                {kv}
              </option>
            ))}
          </select>
        </label>

        <label className="apoema-field">
          Modo de geração
          <select value={value.modo_geracao} onChange={(event) => updateMode(event.target.value as DesignerGenerationMode)} disabled={loading || allowedModes.length === 0}>
            {(allowedModes.length > 0 ? allowedModes : formOptions?.modes ?? []).map((mode) => (
              <option key={mode} value={mode}>
                {mode}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="apoema-designer-template-list" aria-label="Templates disponíveis">
        {templates.length === 0 ? (
          <div className="apoema-empty-state">
            <strong>Sem templates</strong>
            <p>O backend não retornou catálogo disponível.</p>
          </div>
        ) : (
          templates.map((template) => {
            const active = template.template_id === value.template_id;
            return (
              <button key={template.template_id} type="button" className={`apoema-designer-template-card ${active ? "is-active" : ""}`} onClick={() => updateTemplate(template.template_id)}>
                <div className="apoema-designer-template-card-head">
                  <StatusPill tone={active ? "success" : "neutral"}>
                    <Layers3 size={14} />
                    {template.canal}
                  </StatusPill>
                  <StatusPill tone="warning">
                    <Tags size={14} />
                    {template.kv}
                  </StatusPill>
                </div>
                <strong>{template.label}</strong>
                <p>{template.description}</p>
                <small>
                  {template.mode_options.join(" · ")} · prompt {template.prompt_budget} · copy {template.copy_budget}
                </small>
              </button>
            );
          })
        )}
      </div>

      {selectedTemplate ? (
        <div className="apoema-designer-template-summary">
          <StatusPill tone="info">
            <WandSparkles size={14} />
            Template ativo
          </StatusPill>
          <div>
            <strong>{selectedTemplate.label}</strong>
            <p>{selectedTemplate.description}</p>
          </div>
          <small>
            Modos permitidos: {selectedTemplate.mode_options.join(" · ")} · box2 {selectedTemplate.box2_allowed ? "sim" : "não"} · persona image{" "}
            {selectedTemplate.persona_image_allowed ? "sim" : "não"}
          </small>
        </div>
      ) : null}
    </section>
  );
}
