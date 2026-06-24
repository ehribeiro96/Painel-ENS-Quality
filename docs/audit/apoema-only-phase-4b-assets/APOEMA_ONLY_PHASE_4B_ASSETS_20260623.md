# Apoema-only Phase 4B — Assets Migration — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Migrar a entrada legacy `/assets` para Apoema Ativos com paridade mínima comprovada.

## 3. Estado antes
- `/assets`: página legacy no shell antigo.
- `/apoema/assets`: experiência Apoema já existente.
- `/apoema-preview/assets`: alias preservado via rota Apoema.
- `/assets/:id`: detalhe legacy preservado.
- shell legado: ainda responsável pelas rotas antigas.

## 4. Mudança aplicada
`/assets` passou a redirecionar de forma protegida para `/apoema/assets`, preservando a compatibilidade sem renderizar o shell legacy.

## 5. Boundary Apoema-first
O target operacional de Ativos agora vive no `ApoemaApp`.

## 6. Boundary Legacy compatibility
As rotas legadas restantes permanecem no shell antigo, e `/assets/:id` segue disponível.

## 7. O que não foi removido
- `frontend/itam-platform/src/pages/AssetsPage.tsx`
- `frontend/itam-platform/src/App.tsx` legacy compatibility surface

## 8. ProtectedRoute
O alias `/assets` continua protegido.

## 9. Login/Auth
Sem regressão esperada nesta fase.

## 10. Apoema Chat fallback/auth
Sem alteração nesta fase.

## 11. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`
- `.venv/bin/python -m ruff check backend tests scripts`
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build`
- `git diff --check`

## 12. Limitações
`/assets/:id` ainda permanece no fluxo legacy por falta de equivalente no Apoema.

## 13. Próxima fase recomendada
Migrar a superfície de detalhe/ação de ativos, se houver rota Apoema correspondente.
