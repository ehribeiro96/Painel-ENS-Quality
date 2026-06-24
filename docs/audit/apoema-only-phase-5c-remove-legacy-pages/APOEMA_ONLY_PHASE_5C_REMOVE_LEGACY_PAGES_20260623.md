# Apoema-only Phase 5C — Remove Legacy Pages — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Remover páginas legacy não roteadas, sem tocar AppShell, CSS, backend ou assets.

## 3. Estado antes
- Aliases legacy: removidos na Fase 5B.
- Páginas legacy candidatas: DashboardPage, AiChatPage, AssetDetailsPage, AssetsPage, AssignmentsPage, AuditLogsPage, ImportsPage, MacrosPage, SettingsPage, SignaturesPage, StockPage, UserDetailsPage, UsersPage.
- Páginas preservadas: LoginPage, NotFoundPage.

## 4. Manifesto de remoção
Referência: removal-manifest.tsv

## 5. Arquivos removidos
- frontend/itam-platform/src/pages/AiChatPage.tsx
- frontend/itam-platform/src/pages/AssetDetailsPage.tsx
- frontend/itam-platform/src/pages/AssetsPage.tsx
- frontend/itam-platform/src/pages/AssignmentsPage.tsx
- frontend/itam-platform/src/pages/AuditLogsPage.tsx
- frontend/itam-platform/src/pages/DashboardPage.tsx
- frontend/itam-platform/src/pages/ImportsPage.tsx
- frontend/itam-platform/src/pages/MacrosPage.tsx
- frontend/itam-platform/src/pages/SettingsPage.tsx
- frontend/itam-platform/src/pages/SignaturesPage.tsx
- frontend/itam-platform/src/pages/StockPage.tsx
- frontend/itam-platform/src/pages/UserDetailsPage.tsx
- frontend/itam-platform/src/pages/UsersPage.tsx

## 6. Arquivos preservados e justificativa
- LoginPage.tsx
- NotFoundPage.tsx

## 7. AppShell
Preservado.

## 8. CSS global
Não tocado.

## 9. Rotas canônicas
Preservadas em /apoema e /apoema-preview.

## 10. Rotas legacy removidas
Sem aliases legacy no App.tsx desde a Fase 5B.

## 11. Segurança frontend
Sem chamadas diretas a provider e sem secrets expostos nos testes atualizados.

## 12. Smoke HTTP
Executado com resposta 200 nas rotas canônicas e fallback SPA nas rotas removidas.

## 13. Validações
PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v: PASS
.venv/bin/python -m ruff check backend tests scripts: PASS
.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts: PASS
PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build: PASS
git diff --check: PASS

## 14. Limitações
As rotas removidas ainda respondem com fallback SPA no servidor de desenvolvimento; a ausência real foi confirmada por contrato estático e pelo bundle gerado.

## 15. Próxima fase recomendada
Fase 5D: reduzir AppShell legado, se ainda houver superfície restante.
