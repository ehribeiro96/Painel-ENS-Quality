# FRONTEND_M7C_ARTIFACT_UI_UAT_20260630

## 1. Status
GO

## 2. Objetivo
Revalidar a UI Apoema de Artefatos em sessão autenticada, cobrindo listagem, upload, detalhe, download, delete com confirmação, pós-delete, rotas preview e smoke em múltiplos viewports sem expor path interno, storage path, signed token ou signed URL completa.

## 3. Ambiente validado
- Backend runtime: `http://[::1]:8080`
- Frontend runtime: `http://127.0.0.1:5175`
- Sessão autenticada: validada via login UI
- Credencial temporária: `/tmp/painel_runtime_h5_credentials.txt`
- StorageState temporário: `/tmp/m7c-artifact-uat-storage-state.json`

## 4. Resultado funcional
- Login UI: OK
- Listagem `/apoema/artifacts`: OK
- Upload permitido: OK
- Detalhe `/apoema/artifacts/:artifactId`: OK
- Download URL via backend: OK
- Download/open sem signed token visível: OK
- Delete com confirmação: OK
- Pós-delete: OK
- Preview list/detail: OK
- 401 sem token: OK
- 403 com viewer sobre artefato de admin: OK
- 404 pós-delete: OK

## 5. Evidências principais
- Screenshot listagem antes do upload: `docs/audit/frontend-m7c-artifact-ui-uat/screenshots/artifacts-list-1366-before-upload.png`
- Screenshot listagem após upload: `docs/audit/frontend-m7c-artifact-ui-uat/screenshots/artifacts-list-1366-after-upload.png`
- Screenshot detalhe: `docs/audit/frontend-m7c-artifact-ui-uat/screenshots/artifact-detail-1366.png`
- Screenshot preview list: `docs/audit/frontend-m7c-artifact-ui-uat/screenshots/artifacts-preview-list-1366.png`
- Screenshot preview detail: `docs/audit/frontend-m7c-artifact-ui-uat/screenshots/artifact-preview-detail-1366.png`

## 6. Segurança validada
- Path interno exposto: não
- Storage path exposto: não
- Signed token visível/logado: não
- Signed URL completa logada: não
- StorageState/cookies/tokens commitados: não
- Alias legacy `/artifacts`: não
- AppShell legado restaurado: não

## 7. Observações
- O fluxo de upload foi validado com um arquivo TXT temporário criado fora do repositório.
- A UI de lista após upload e a página de detalhe não exibem campos internos de storage.
- O download foi validado pelo backend com fetch do link temporário e abertura em popup sem registrar a URL completa.

## 8. Relatório resumido dos gates
Ver `frontend-m7c-artifact-ui-uat-gates.log`.

## 9. Próxima fase recomendada
`FRONTEND_M7D_ARTIFACT_UI_PUSH_PREP`
