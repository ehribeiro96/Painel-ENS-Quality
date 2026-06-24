# Apoema-only Phase 5D — Remove AppShell — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Remover o AppShell legado sem tocar CSS, backend, assets ou páginas preservadas.

## 3. Estado antes
- AppShell: presente, mas sem uso ativo no roteamento.
- App.tsx: já operava em Apoema-first sem LegacyRoutes.
- Rotas canônicas: `/`, `/login`, `/apoema/*`, `/apoema-preview/*`.
- Aliases legacy: já removidos na Fase 5B.
- Páginas legacy: já removidas na Fase 5C.

## 4. Manifesto de remoção
Referência: APPSHELL_REMOVAL_MANIFEST_20260623.tsv

## 5. Mudança aplicada
- `frontend/itam-platform/src/components/AppShell.tsx` removido do tree.
- `frontend/itam-platform/src/App.tsx` permanece sem shell legado.
- Contratos atualizados para refletir ausência do shell legado.

## 6. AppShell removido ou preservado
Removido.

## 7. Justificativa
Não havia mais referência de runtime para o shell legado; o roteamento já estava isolado em Apoema-first e os testes cobrindo a ausência de aliases/shell passaram.

## 8. CSS global
Preservado.

## 9. Login e NotFound
Preservados.

## 10. Rotas canônicas Apoema
Preservadas e validadas.

## 11. Segurança frontend
Sem chamada direta a provider e sem secrets versionados encontrados.

## 12. Smoke HTTP
Vite respondeu 200 nas rotas canônicas. Os aliases removidos também retornaram 200 por fallback de SPA, o que não prova alias ativo; a ausência foi confirmada por `App.tsx`, bundle e contratos.

## 13. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`
- `.venv/bin/python -m ruff check backend tests scripts`
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build`
- `git diff --check`

## 14. Limitações
O smoke HTTP em Vite dev usa fallback de SPA e responde 200 para rotas removidas; por isso a remoção foi confirmada por contratos estáticos e bundle.

## 15. Próxima fase recomendada
Fase 5E: isolar ou reduzir CSS legacy com boundary explícita.
