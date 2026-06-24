# Apoema-only Phase 5B — Remove Legacy Aliases — 2026-06-23

## 1. Status
PARTIAL-GO:

## 2. Objetivo
Remover aliases legacy do roteamento, sem apagar arquivos legacy.

## 3. Estado antes
- Rotas canônicas Apoema: `/apoema`, `/apoema/*`, `/login`, `/apoema-preview`, `/apoema-preview/*`
- Aliases legacy: `/ai-chat`, `/assets`, `/assets/:id`, `/audit-logs`, `/imports`, `/macros`, `/stock`, `/signatures`, `/assignments`, `/users`, `/users/:id`, `/settings`
- AppShell: ainda existe no código, mas não é alcançado por rotas migradas
- Componentes legacy: permanecem em disco para compatibilidade e fases futuras

## 4. Mudança aplicada
Removi do `App.tsx` os aliases legacy que ainda apontavam para Apoema. Mantive a entrada canônica `/` redirecionando para `/apoema`, preservei `/login`, `/apoema`, `/apoema/*`, `/apoema-preview` e `/apoema-preview/*`, e deixei `LegacyRoutes` sem rotas ativas.

## 5. Aliases removidos
- `/ai-chat`
- `/assets`
- `/assets/:id`
- `/audit-logs`
- `/imports`
- `/macros`
- `/stock`
- `/signatures`
- `/assignments`
- `/users`
- `/users/:id`
- `/settings`

## 6. Aliases preservados e justificativa
- `/` preservado como entrada raiz canônica que redireciona para `/apoema`
- `/login` preservado porque é a rota de autenticação real
- `/apoema-preview` e `/apoema-preview/*` preservados como alias técnico de preview

## 7. Rotas canônicas preservadas
- `/apoema`
- `/apoema/*`
- `/login`
- `/apoema-preview`
- `/apoema-preview/*`

## 8. AppShell
AppShell não foi removido. Ele segue fora da superfície principal e permanece apenas como boundary legado.

## 9. Componentes legacy
Os arquivos legacy continuam no disco, mas sem aliases de roteamento ativos para a superfície Apoema.

## 10. CSS global
Não alterado nesta fase.

## 11. Segurança frontend
Sem chamadas diretas a provider e sem secrets versionados detectados nos contratos revisados.

## 12. Smoke HTTP
O smoke HTTP foi executado com `curl` contra o Vite local. O servidor devolve o SPA HTML com `200` para os paths consultados, então a remoção dos aliases foi confirmada de forma mais forte pelos contratos de código e pela ausência dos aliases no bundle gerado.

## 13. Validações
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`
- `.venv/bin/python -m ruff check backend tests scripts`
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `npm run build`
- `git diff --check`
- `curl` smoke em rotas canônicas e legacy
- scan do bundle gerado para confirmar ausência dos aliases removidos

## 14. Limitações
Não houve browser automation disponível nesta thread para confirmar visualmente o `NotFound` client-side nas rotas removidas. O bundle e os contratos estáticos cobrem o estado esperado.

## 15. Próxima fase recomendada
Fase 5C: remover componentes legacy não roteados, se continuar sem regressão.
