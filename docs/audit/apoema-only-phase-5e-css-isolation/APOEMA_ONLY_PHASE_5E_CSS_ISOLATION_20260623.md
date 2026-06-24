# Apoema-only Phase 5E — CSS Isolation — 2026-06-23

## 1. Status
GO:

## 2. Objetivo
Isolar e reduzir CSS legado sem quebrar visual Apoema, Login ou NotFound.

## 3. Estado antes
- AppShell: já removido.
- Páginas legacy: já removidas.
- styles.css: ainda concentrava blocos globais de shell e páginas antigas.
- Apoema CSS: já isolado em `frontend/itam-platform/src/apoema/styles/apoema.css`.
- Login/NotFound: preservados e dependentes de base global mínima.

## 4. Inventário CSS
Referência: CSS_SELECTOR_INVENTORY_20260623.tsv

## 5. Manifesto de alteração
Referência: CSS_ISOLATION_MANIFEST_20260623.tsv

## 6. Mudanças aplicadas
- Removidos blocos globais antigos de shell e chrome legado.
- Removidos helpers de layout de páginas antigas já não roteadas.
- Preservados estilos ativos usados por Apoema, Login, NotFound e diálogos operacionais.

## 7. Seletores removidos
- Shell e chrome legado sem consumidor atual.
- Helpers de páginas antigas sem rota.
- `wide-field` foi preservado porque permanece em uso no fluxo de movimentações.

## 8. Seletores preservados
- `:root`, `body`, `.grid`, `.detail-grid`, `.metrics`, `.form-grid`, `.mapping-grid`
- `.filter-bar`, `.ops-panel`, `.action-bar`, `.assignments-toolbar`
- `.wide-field`, `.details`, `.metric-card`, `.filter-chip`, `.email-cell`, `.users-row-actions`
- `.base44-login-shell`, `.base44-notfound-shell`

## 9. Seletores movidos/isolados
Nenhum bloco foi convertido para CSS Modules nesta fase.

## 10. CSS global residual
Permanece um núcleo global mínimo para suporte das rotas preservadas e componentes compartilhados.

## 11. Risco visual restante
Baixo a médio. O corte foi conservador e manteve seletores ainda consumidos pelo frontend atual, inclusive o helper `wide-field`.

## 12. Login e NotFound
Preservados.

## 13. Rotas canônicas Apoema
Preservadas.

## 14. Segurança frontend
Sem chamadas diretas a provider e sem secrets versionados encontrados.

## 15. Smoke HTTP
Executado com Vite dev. O servidor já ocupava `18086`, então a nova instância subiu em `18092`. As rotas canônicas responderam 200.

## 16. Smoke visual
Não executado nesta rodada.

## 17. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`
- `.venv/bin/python -m ruff check backend tests scripts`
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build`
- `git diff --check`

## 18. Limitações
Alguns blocos globais antigos continuam no arquivo por segurança de preservação visual. A fase reduziu o risco, mas não faz uma limpeza total.

## 19. Próxima fase recomendada
Fase 5F: fazer auditoria visual final e, se estável, continuar reduzindo CSS legado residual.
