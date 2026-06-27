# M6B Apoema UI Stubs — 2026-06-26

## 1. Status

GO. UI stubs criados e validados para Artifacts, RAG e Designer, preservando a boundary M6 READY_FOR_UI_STUBS.

## 2. Objetivo

Expor entradas controladas no Apoema para adapters já validados: Artifacts API operacional, AI Chat API operacional, RAG API mock operacional e Designer API mock operacional.

## 3. Base M6 GO

Base confirmada no commit `133d236`: status GO, storageState fora do repositório, browser auth validado, rotas Apoema sem redirect para login e API smoke autenticado OK para Artifacts, AI Chat, RAG e Designer.

## 4. O que foi implementado

- Clients frontend backend-only para `/api/v1/artifacts`, `/api/v1/rag/*` e `/api/v1/designer/*`.
- Páginas Apoema `ArtifactsPage`, `RagPage` e `DesignerPage`.
- Navegação Apoema com rótulos Artefatos, RAG e Designer, incluindo badges Backend/Mock/Beta controlado.
- Copy de segurança em `IntegrationsPage`.
- Testes de contrato para rotas, ausência de aliases legacy, boundary provider/mock e storageState fora do repo.

## 5. Rotas Apoema criadas

- `/apoema/artifacts`
- `/apoema/rag`
- `/apoema/designer`
- `/apoema-preview/artifacts` via wildcard controlado existente
- `/apoema-preview/rag` via wildcard controlado existente
- `/apoema-preview/designer` via wildcard controlado existente

Aliases legacy `/artifacts`, `/rag`, `/designer` e `/files` não foram criados.

## 6. UI Artifacts

A página Biblioteca de Artefatos mostra status “Backend Artifact Storage”, aviso de storage backend-owned, listagem, upload, obtenção de link assinado, cópia de URL assinada sem console log e exclusão. A UI não mostra path interno e não faz preview de conteúdo sensível.

## 7. UI RAG

A página RAG MCP Mock mostra status “Mock determinístico”, aviso de que MCP real, vector store e provider real não estão ativos, collections, busca, resultados com citações mock, contexto de curso controlado e auditoria recente.

## 8. UI Designer

A página Designer Mock mostra status “Mock determinístico”, health/templates/form-options, formulário controlado e criação de job determinístico. Ações adjust, refresh-url e cancel chamam apenas backend; download-url bloqueado/não disponível fica explícito.

## 9. Mock/provider safety

Não foi adicionado provider real, MCP real, vector store real, geração real de imagem nem provider key no frontend. Os clients novos usam `const API_BASE = "/api/v1"` e fetch relativo.

## 10. Auth/Playwright

Playwright autenticado foi executado com storageState em `/tmp/apoema-uat-auth-state.json` e screenshots em `screenshots/`. Matrix: `27` rotas/viewports, falhas `0`, erros fatais `0`.

## 11. Validações

- `PYTHONPATH=backend .venv/bin/python -m pytest tests/test_apoema_ui_stubs_contract.py tests/test_apoema_no_direct_provider_contract.py`: 11 passed.
- `PYTHONPATH=backend .venv/bin/python -m pytest`: 336 passed, 22 skipped.
- `.venv/bin/python -m ruff check backend tests scripts`: All checks passed.
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: exit 0.
- `npm run build`: passou; CSS principal gerado `61.40 kB` gzip `11.01 kB`.
- Playwright autenticado: passou após regenerar storageState fora do repo e evitar rotação excessiva em navegações full reload.

## 12. Screenshots

Foram criados 27 screenshots autenticados. Exemplos:

- `screenshots/1366x768-apoema-preview_artifacts.png`
- `screenshots/1366x768-apoema-preview_designer.png`
- `screenshots/1366x768-apoema-preview_rag.png`
- `screenshots/1366x768-apoema.png`
- `screenshots/1366x768-apoema_artifacts.png`
- `screenshots/1366x768-apoema_chat.png`
- `screenshots/1366x768-apoema_designer.png`
- `screenshots/1366x768-apoema_rag.png`
- `screenshots/1366x768-apoema_settings.png`
- `screenshots/1920x1080-apoema-preview_artifacts.png`
- `screenshots/1920x1080-apoema-preview_designer.png`
- `screenshots/1920x1080-apoema-preview_rag.png`

Lista completa em `maps/visual-smoke-matrix.tsv`.

## 13. O que não foi implementado

- Provider real.
- MCP runtime real.
- Vector store real.
- Geração real de imagem.
- Rotas legacy fora de `/apoema`.
- Mudanças backend, Docker, migrations, AuthProvider ou ProtectedRoute.

## 14. Riscos restantes

- UAT funcional de upload/exclusão/cópia ainda deve ser exercido manualmente na próxima fase com massa controlada.
- RAG e Designer seguem mocks determinísticos; qualquer ativação real precisa nova boundary e revisão de segredo/provider.
- Auth storageState tem rotação por refresh; smokes devem preservar state atualizado e evitar reloads excessivos para não acionar rate limit.

## 15. Próxima fase recomendada

M6C_APOEMA_UI_STUBS_UAT.
