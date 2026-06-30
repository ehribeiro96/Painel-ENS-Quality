# Frontend M7B - Artifact UI Implementation

## 1. Status
GO

## 2. Escopo
Implementar a interface Apoema de Artefatos sobre o backend Artifact real, mantendo storage privado backend-owned e sem criar alias legado.

## 3. Arquivos alterados
- `frontend/itam-platform/src/apoema/ApoemaApp.tsx`
- `frontend/itam-platform/src/apoema/pages/ArtifactsPage.tsx`
- `frontend/itam-platform/src/apoema/pages/ArtifactDetailPage.tsx`
- `frontend/itam-platform/src/apoema/lib/apoemaArtifactsApi.ts`
- `frontend/itam-platform/src/apoema/types.ts`
- `frontend/itam-platform/src/apoema/styles/apoema.css`
- `tests/test_apoema_artifacts_ui_contract.py`

## 4. Rotas
- `/apoema/artifacts`
- `/apoema/artifacts/:artifactId`
- `/apoema-preview/artifacts`
- `/apoema-preview/artifacts/:artifactId`

Nenhuma rota top-level `/artifacts` foi adicionada.

## 5. Endpoints consumidos
- `POST /api/v1/artifacts`
- `GET /api/v1/artifacts`
- `GET /api/v1/artifacts/{artifact_id}`
- `GET /api/v1/artifacts/{artifact_id}/download-url`
- `DELETE /api/v1/artifacts/{artifact_id}`

O download continua mediado pelo backend por URL temporaria gerada sob demanda.

## 6. UI implementada
- Lista com nome, MIME, tamanho, origem/status, data e acoes.
- Busca client-side por nome, MIME, ID ou SHA-256.
- Upload via `FormData`.
- Pagina de detalhe com metadata segura.
- Download por chamada ao backend e abertura direta da URL retornada.
- Delete com confirmacao explicita.
- Estados 401, 403, 404, 410, erro de rede, loading, empty e erro generico.

## 7. Seguranca
- Sem chamada direta a storage.
- Sem path interno de storage na UI.
- Sem renderizacao de token temporario cru.
- Sem persistencia local de URL temporaria.
- Sem `console.log` ou `console.error` para URLs.
- Sem AppShell legado.
- Sem alias legado `/artifacts`.

## 8. Limitacoes
- A busca e client-side porque o contrato backend atual nao expoe query params.
- A UI nao implementa preview de conteudo do arquivo.
- Smoke HTTP local pode ser pulado se runtime Vite nao estiver ativo.

## 9. Gates
Resultados registrados em `frontend-m7b-artifact-ui-gates.log`.

## 10. Smoke HTTP
O helper `scripts/dev-apoema-vite.sh` existe, mas `http://127.0.0.1:5175` nao respondeu aos `curl -I` dentro do timeout local durante esta fase. Como `npm run build` e os testes passaram, o smoke HTTP ficou registrado como runtime local indisponivel/timeout, sem bloquear a decisao.

## 11. Push
Push executado: nao.

## 12. Proxima fase
`FRONTEND_M7C_ARTIFACT_UI_UAT`
