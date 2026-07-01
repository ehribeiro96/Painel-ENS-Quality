import { ArrowRight, FileText, Palette, PencilLine, ShieldAlert, Sparkles } from "lucide-react";
import { StatusPill } from "./StatusPill";
import { DesignerTemplateSelector, type DesignerSelection } from "./DesignerTemplateSelector";
import type { DesignerBannerJsonRequest, DesignerFormOptions, DesignerTemplate } from "../types";

type DesignerBannerDraft = Pick<
  DesignerBannerJsonRequest,
  "template_id" | "modo_geracao" | "prompt" | "copy" | "box2" | "item_count"
> & {
  canal: string;
  kv: string;
};

type Props = {
  templates: DesignerTemplate[];
  formOptions: DesignerFormOptions | null;
  value: DesignerBannerDraft;
  onChange: (next: DesignerBannerDraft) => void;
  onSubmit: () => void | Promise<void>;
  disabled?: boolean;
  loading?: boolean;
  catalogLoading?: boolean;
  banner?: string | null;
};

export function DesignerBannerForm({ templates, formOptions, value, onChange, onSubmit, disabled = false, loading = false, catalogLoading = false, banner = null }: Props) {
  const selection: DesignerSelection = {
    template_id: value.template_id,
    canal: value.canal,
    kv: value.kv,
    modo_geracao: value.modo_geracao,
  };

  function updateSelection(next: DesignerSelection) {
    onChange({ ...value, ...next });
  }

  return (
    <section className="apoema-designer-form">
      <div className="apoema-section-head">
        <div>
          <StatusPill tone="warning">
            <Sparkles size={14} />
            Geração JSON
          </StatusPill>
          <h2>Criar job</h2>
          <p>O backend mock/determinístico recebe somente JSON. Upload de imagem, provider real e download-url seguem indisponíveis nesta fase.</p>
        </div>
        <span>{loading ? "Enviando" : "Pronto"}</span>
      </div>

      {banner ? (
        <div className="apoema-warning is-warning">
          <ShieldAlert size={16} />
          <div>
            <strong>Observação</strong>
            <p>{banner}</p>
          </div>
        </div>
      ) : null}

      <DesignerTemplateSelector
        templates={templates}
        formOptions={formOptions}
        value={selection}
        onChange={updateSelection}
        loading={catalogLoading}
      />

      <div className="apoema-designer-field-grid">
        <label className="apoema-field">
          <span>
            <FileText size={14} />
            Briefing
          </span>
          <textarea
            value={value.prompt}
            onChange={(event) => onChange({ ...value, prompt: event.target.value })}
            rows={6}
            placeholder="Descreva o banner, público-alvo, CTA e contexto do job."
            disabled={disabled}
            maxLength={formOptions?.max_prompt_length}
          />
        </label>

        <label className="apoema-field">
          <span>
            <Palette size={14} />
            Texto / copy
          </span>
          <textarea
            value={value.copy ?? ""}
            onChange={(event) => onChange({ ...value, copy: event.target.value })}
            rows={4}
            placeholder="Opcional. Se vazio, o backend usará o prompt."
            disabled={disabled}
            maxLength={formOptions?.max_copy_length}
          />
        </label>

        <label className="apoema-field">
          <span>
            <PencilLine size={14} />
            Box2
          </span>
          <textarea
            value={value.box2 ?? ""}
            onChange={(event) => onChange({ ...value, box2: event.target.value })}
            rows={4}
            placeholder="Opcional. Refinamento adicional para o mock determinístico."
            disabled={disabled}
            maxLength={formOptions?.max_copy_length}
          />
        </label>

        <label className="apoema-field apoema-designer-field-number">
          <span>Quantidade de itens</span>
          <input
            type="number"
            min={1}
            max={formOptions?.max_items_per_job ?? 12}
            value={value.item_count}
            onChange={(event) => onChange({ ...value, item_count: Number(event.target.value) || 1 })}
            disabled={disabled}
          />
        </label>
      </div>

      <div className="apoema-designer-note">
        <strong>Contrato honesto</strong>
        <p>Sem provider real, sem download-url e sem integração com Artifact/Chat/RAG. O frontend apenas orquestra /api/v1/designer.</p>
      </div>

      <div className="apoema-designer-form-actions">
        <small>
          Campos máximos: prompt {formOptions?.max_prompt_length ?? 0}, copy {formOptions?.max_copy_length ?? 0}, itens por job {formOptions?.max_items_per_job ?? 0}
        </small>
        <button type="button" className="apoema-primary-button" disabled={disabled || !value.template_id || !value.canal || !value.kv || !value.modo_geracao} onClick={() => void onSubmit()}>
          <ArrowRight size={16} />
          {loading ? "Criando job..." : "Criar job"}
        </button>
      </div>
    </section>
  );
}
