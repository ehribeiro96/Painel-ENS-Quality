# ENS Unified Migration M6 — Authenticated E2E and UI Gate

## 1. Status
PARTIAL_GO

## 2. Objetivo
Validar runtime, auth, adapters mockados e decisão de gate antes de qualquer UI nova.

## 3. Base consolidada
- M1C: GO
- M2B: GO
- M3B: GO
- M4B: GO

## 4. Runtime analisado
- Backend: http://localhost:8080
- Frontend: http://127.0.0.1:5175 (Vite dev server)
- Rebuild/restart: sim
- OpenAPI: todas as rotas requeridas presentes

## 5. Backend route gate
Arquivo: maps/backend-route-gate.tsv

## 6. Auth gate sem token
Artifacts, AI Chat, RAG e Designer retornaram 401 missing_token no runtime atual.

## 7. Sessão UAT
- Storage state validado em /tmp/apoema-uat-auth-state.json
- Authenticated session: sim

## 8. API smoke autenticado
Arquivo: maps/authenticated-api-smoke.tsv

## 9. Playwright autenticado
Arquivo: maps/visual-route-matrix.tsv

## 10. Evidência visual
Screenshots gerados em: screenshots/

## 11. Segurança
- provider real: não
- MCP runtime real: não
- vector store real: não
- image generation real: não
- storageState committed: não
- secrets found: não

## 12. UI gate decision
PARTIAL_READY_BACKEND_ONLY

## 13. O que NÃO foi implementado
- UI nova no Apoema
- atalhos novos no Apoema
- provider real
- MCP real
- vector store real
- geração real de imagem

## 14. Validações
- OpenAPI no código atual conferido
- runtime live atualizado com rebuild controlado
- smoke sem token: 401 missing_token em todos os módulos requeridos
- smoke autenticado via storageState
- rota visual autenticada nos viewports definidos

## 15. Limitações
- O fluxo foi validado com auth state local em /tmp, não persistido no repositório.

## 16. Próxima fase recomendada
M6B_APOEMA_UI_STUBS
