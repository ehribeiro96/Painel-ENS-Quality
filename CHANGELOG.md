# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo.

## v1.0.0-rc1 — 2026-07-20

### Adicionado

- Governança de IA por capabilities para Chat, Macros, Imports e configuração de providers.
- Auditoria persistente das operações e falhas de IA.
- Geração de Macros ITIL vinculada à movimentação salva.
- Análise de Imports por IA com sugestões sujeitas a aprovação ou rejeição humana.
- Migration `0007_macro_movement_unique` e cobertura de idempotência.
- Suíte crítica determinística no workflow de quality gates.

### Alterado

- RBAC de usuários e limites de permissão para `ADMIN`, `TECHNICIAN` e `VIEWER`.
- Health público sanitizado, separado em liveness e readiness.
- Frontend operacional de Chat, Macros e Imports.
- Dependências do frontend compatíveis com Vite 6.4.3.
- Lifecycle de autenticação e refresh no frontend.

### Corrigido

- Bloqueio de `VIEWER` antes da chamada ao provider de IA.
- Remoção do fallback mock automático no caminho Hermes candidato a produção.
- Timeout Hermes mapeado para HTTP 502.
- Persistência de falhas de IA em transação independente.
- Idempotência concorrente de macro por movimentação.

### Validação

- Suíte completa pytest e suíte crítica de segurança.
- Ruff no escopo canônico `backend tests scripts`.
- Compileall de backend, migrations, testes e scripts.
- Build Vite, Docker Compose, Alembic e smoke de runtime.
