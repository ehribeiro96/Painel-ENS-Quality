import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Alert } from "@/components/StateBlocks";
import { api } from "@/lib/api";
import type { Asset, AssetStatus, Page, SuggestedMovementMacro, User } from "@/lib/types";

const moveSchema = z
  .object({
    new_user_id: z.string().optional(),
    new_status: z.enum(["IN_USE", "STOCK", "MAINTENANCE", "DEFECTIVE", "DISCARDED", "RESERVED", "CONFIG_PENDING"]),
    new_location: z.string().max(160).optional(),
    justification: z.string().min(5, "Informe uma justificativa com pelo menos 5 caracteres.").max(500),
    notes: z.string().max(2000).optional(),
    explicit_confirmation: z.boolean()
  })
  .refine((value) => value.new_status !== "IN_USE" || Boolean(value.new_user_id), {
    path: ["new_user_id"],
    message: "Usuario e obrigatorio para status IN_USE."
  })
  .refine((value) => value.explicit_confirmation, {
    path: ["explicit_confirmation"],
    message: "Confirme explicitamente a movimentação."
  });

type MoveForm = z.infer<typeof moveSchema>;

type MoveAssetDialogProps = {
  asset: Asset | null;
  token: string;
  users?: Page<User> | null;
  onClose: () => void;
  onMoved: () => void;
};

const statuses: AssetStatus[] = ["IN_USE", "STOCK", "MAINTENANCE", "DEFECTIVE", "DISCARDED", "RESERVED", "CONFIG_PENDING"];

export function MoveAssetDialog({ asset, token, users, onClose, onMoved }: MoveAssetDialogProps) {
  const [isSubmittingMovement, setIsSubmittingMovement] = useState(false);
  const [movementResult, setMovementResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [generatedMacro, setGeneratedMacro] = useState<SuggestedMovementMacro | null>(null);
  const [isCopyingMacro, setIsCopyingMacro] = useState(false);
  const [macroCopied, setMacroCopied] = useState(false);

  const form = useForm<MoveForm>({
    resolver: zodResolver(moveSchema),
    defaultValues: {
      new_user_id: asset?.current_user_id ?? "",
      new_status: asset?.status ?? "STOCK",
      new_location: asset?.location ?? "",
      justification: "",
      notes: "",
      explicit_confirmation: false
    }
  });

  const watched = form.watch();
  const selectedUser = useMemo(
    () => users?.items.find((user) => user.id === watched.new_user_id),
    [users?.items, watched.new_user_id]
  );

  useEffect(() => {
    if (!asset) {
      return;
    }
    form.reset({
      new_user_id: asset.current_user_id ?? "",
      new_status: asset.status ?? "STOCK",
      new_location: asset.location ?? "",
      justification: "",
      notes: "",
      explicit_confirmation: false
    });
    setMovementResult(null);
    setError(null);
    setGeneratedMacro(null);
    setIsCopyingMacro(false);
    setMacroCopied(false);
  }, [asset?.id, form]);

  if (!asset) {
    return null;
  }

  async function submit(values: MoveForm) {
    if (!asset || isSubmittingMovement || generatedMacro) {
      return;
    }
    setIsSubmittingMovement(true);
    setError(null);
    setMovementResult(null);
    try {
      const movement = await api.moveAsset(token, asset.id, {
        new_user_id: values.new_user_id || null,
        new_status: values.new_status,
        new_location: values.new_location || null,
        justification: values.justification,
        notes: values.notes || null
      });
      const suggested = await api.suggestedMovementMacro(token, movement.id).catch(() => null);
      setGeneratedMacro(suggested?.rendered_text ? suggested : null);
      setMacroCopied(false);
      setMovementResult("Movimentação registrada com sucesso. Histórico atualizado.");
      onMoved();
    } catch {
      setError("Não foi possível movimentar o ativo. Revise os campos e tente novamente.");
    } finally {
      setIsSubmittingMovement(false);
    }
  }

  async function copyGeneratedMacro() {
    if (!generatedMacro?.generation_id || isCopyingMacro) {
      return;
    }
    setIsCopyingMacro(true);
    setError(null);
    try {
      await navigator.clipboard.writeText(generatedMacro.rendered_text);
      await api.macroMarkCopied(token, generatedMacro.generation_id);
      setMacroCopied(true);
    } catch {
      setError("Não foi possível copiar a macro. Tente novamente.");
    } finally {
      setIsCopyingMacro(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="modal" role="dialog" aria-modal="true" aria-labelledby="move-asset-title">
        <div className="page-title compact">
          <div>
            <h1 id="move-asset-title">Movimentar ativo</h1>
            <p>{asset.hostname ?? asset.patrimony ?? asset.serial ?? asset.id}</p>
          </div>
          <button className="icon-only" type="button" aria-label="Fechar movimentação" onClick={onClose}>X</button>
        </div>

        {movementResult ? <Alert tone="success">{movementResult}</Alert> : null}
        {error ? <Alert tone="danger">{error}</Alert> : null}
        {generatedMacro ? (
          <div className="macro-after-move">
            <h2>Macro de movimentação</h2>
            {generatedMacro.pending_fields.length > 0 ? (
              <Alert tone="danger">Campos pendentes: {generatedMacro.pending_fields.join(", ")}. Revise antes de colar no chamado.</Alert>
            ) : null}
            {macroCopied ? <Alert tone="success">Macro copiada.</Alert> : null}
            <textarea className="textarea macro-preview" readOnly rows={7} value={generatedMacro.rendered_text} />
            <button
              className="button secondary"
              type="button"
              disabled={!generatedMacro.generation_id || isCopyingMacro}
              onClick={() => void copyGeneratedMacro()}
            >
              {generatedMacro.generation_id ? (isCopyingMacro ? "Copiando..." : "Copiar macro") : "Erro: Macro não persistida"}
            </button>
          </div>
        ) : null}

        <div className="compare-grid">
          <article className="state-card current">
            <h2>Atual</h2>
            <dl className="details">
              <dt>Usuário</dt><dd>{asset.current_user?.name ?? "Sem usuário"}</dd>
              <dt>Status</dt><dd><span className="badge">{asset.status}</span></dd>
              <dt>Local</dt><dd>{asset.location ?? "-"}</dd>
            </dl>
          </article>
          <article className="state-card next">
            <h2>Novo</h2>
            <dl className="details">
              <dt>Usuário</dt><dd>{selectedUser?.name ?? "Sem usuário"}</dd>
              <dt>Status</dt><dd><span className="badge">{watched.new_status}</span></dd>
              <dt>Local</dt><dd>{watched.new_location || "-"}</dd>
            </dl>
          </article>
        </div>

        <form className="form-grid" onSubmit={form.handleSubmit(submit)}>
          <label>
            Novo usuário
            <select className="select full" {...form.register("new_user_id")}>
              <option value="">Sem usuário</option>
              {users?.items.map((user) => (
                <option key={user.id} value={user.id}>{user.name} - {user.email}</option>
              ))}
            </select>
            {form.formState.errors.new_user_id ? <span className="field-error">{form.formState.errors.new_user_id.message}</span> : null}
          </label>
          <label>
            Novo status
            <select className="select full" {...form.register("new_status")}>
              {statuses.map((status) => <option key={status} value={status}>{status}</option>)}
            </select>
          </label>
          <label>
            Nova localidade
            <input className="input full" {...form.register("new_location")} />
          </label>
          <label>
            Justificativa
            <input className="input full" {...form.register("justification")} placeholder="Ex.: troca de colaborador, manutencao, estoque" />
            {form.formState.errors.justification ? <span className="field-error">{form.formState.errors.justification.message}</span> : null}
          </label>
          <label className="span-2">
            Observacoes
            <textarea className="textarea" {...form.register("notes")} rows={3} />
          </label>
          <label className="confirm-line span-2">
            <input type="checkbox" {...form.register("explicit_confirmation")} />
            Confirmo que revisei usuário, status e localidade antes de registrar a movimentação.
          </label>
          {form.formState.errors.explicit_confirmation ? <span className="field-error span-2">{form.formState.errors.explicit_confirmation.message}</span> : null}
          <div className="modal-actions span-2">
            <button className="button secondary" type="button" onClick={onClose} disabled={isSubmittingMovement}>{generatedMacro ? "Concluir" : "Cancelar"}</button>
            <button className="button" type="submit" disabled={isSubmittingMovement || Boolean(generatedMacro)}>
              {isSubmittingMovement ? "Registrando..." : generatedMacro ? "Movimentação registrada" : "Confirmar movimentação"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
