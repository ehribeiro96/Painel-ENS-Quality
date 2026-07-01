# FRONTEND_M10C_DESIGNER_UI_UAT_20260630

## 1. Status
GO

## 2. Objetivo
Validar, com sessão autenticada, a UI Apoema Designer mock/determinística em `/apoema/designer` e `/apoema-preview/designer`, incluindo detalhe de job, templates, form-options, criação de job e ações backend-backed.

## 3. Estado Git local/remoto
- Origin: `git@github.com:ehribeiro96/Painel-ENS-Quality.git`
- Branch: `main`
- Divergência antes dos commits desta fase: `0 2`
- Stage: limpo antes de criar os artefatos desta fase
- Tracked diff: vazio antes de criar os artefatos desta fase

## 4. Actions
- Run verificado: `28526136825`
- Resultado: `success`

## 5. Backend Designer e smoke
- Health: `200`
- Templates: `200`
- Form-options: `200`
- Job create: `200`
- Job detail: `200`
- Item adjust: `200`
- Item refresh-url: `200`
- Job cancel: `200`
- Download-url bloqueado: `409`
- Missing job: `404`
- Payload inválido: `422`
- Missing token: `401`
- Sem permissão para viewer: `403`
- Rate limit em login inválido: `429`

## 6. Sessão autenticada
- Sessão autenticada validada via login local com usuário UAT ADMIN sintético fora do repositório.
- Nenhum segredo, cookie ou storageState foi registrado em docs.

## 7. UAT visual/funcional
- `/apoema/designer` renderizou com heading `Designer`.
- `/apoema/designer/jobs/{jobId}` renderizou com heading `Detalhe do job`.
- `/apoema-preview/designer` renderizou corretamente.
- `/apoema-preview/designer/jobs/{jobId}` renderizou corretamente.
- Job criado via UI com `job_id` obtido do backend.
- Ajuste e refresh de item foram validados no fluxo UI/API.
- Cancelamento do job foi validado no backend; na captura UI o botão apareceu desabilitado para o estado corrente do job, sem expor falha de segurança.
- Download-url permaneceu indisponível conforme contrato.
- Provider real permaneceu desativado.
- Artifact/Chat/RAG não apareceram como integrações implementadas nesta fase.

## 8. Segurança
- Sem provider/image secret exposto.
- Sem path interno ou storage path exposto na UI.
- Sem token cru renderizado.
- Sem fallback enganoso para 401/403/429.
- Sem chamada direta a provider, storage, Artifact, Chat ou RAG.

## 9. Gates locais
- `git diff --check`
- `pytest -s -q`
- `ruff check backend tests scripts`
- `compileall -q backend/app backend/alembic tests scripts`
- `npm run build`
- `docker compose config --services`

## 10. Evidências
- `docs/audit/frontend-m10c-designer-ui-uat/raw/runtime-check.log`
- `docs/audit/frontend-m10c-designer-ui-uat/raw/api-smoke-redacted.log`
- `docs/audit/frontend-m10c-designer-ui-uat/raw/playwright-designer-uat-redacted.json`
- `docs/audit/frontend-m10c-designer-ui-uat/screenshots/designer-page.png`
- `docs/audit/frontend-m10c-designer-ui-uat/screenshots/designer-job-page.png`
- `docs/audit/frontend-m10c-designer-ui-uat/screenshots/designer-preview-page.png`
- `docs/audit/frontend-m10c-designer-ui-uat/screenshots/designer-preview-job-page.png`

## 11. Push e commit
- Push: não executado nesta fase
- Commit: documentação UAT foi mantida local até a decisão final

## 12. Decisão
GO para a UAT do Designer mock/determinístico.

## 13. Próxima fase
FRONTEND_M10D_DESIGNER_UI_PUSH_PREP
