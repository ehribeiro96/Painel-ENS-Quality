# Operational Test Matrix

Data: 2026-06-01

Esta matriz cobre a regressao operacional minima para os fluxos criticos validados com Docker, PostgreSQL e Redis.

| ID | Nome | Objetivo | Pre-condicao | Comando | Resultado esperado | Criticidade | Tipo | Status |
|---|---|---|---|---|---|---|---|---|
| AUTH-001 | Login valido | Validar credenciais admin | `ADMIN_PASSWORD` local definido | `python -m unittest tests.test_auth_regression` | 200 e access token | Critico | integration/docker | automated |
| AUTH-002 | Login invalido | Garantir rejeicao segura | App ativo | `python -m unittest tests.test_auth_regression` | 401 | Alto | integration/docker | automated |
| AUTH-003 | `/me` autenticado | Validar sessao JWT | Login valido | `python -m unittest tests.test_auth_regression` | 200 e email correto | Critico | integration/docker | automated |
| AUTH-004 | Refresh token | Validar cookie HttpOnly/refresh | Login valido | `python -m unittest tests.test_auth_regression` | Novo access token | Critico | integration/docker | automated |
| AUTH-005 | Logout | Validar revogacao/limpeza | Login valido | `python -m unittest tests.test_auth_regression` | 200 e refresh posterior 401 | Critico | integration/docker | automated |
| AUTH-006 | Protegida sem token | Confirmar seguranca padrao | App ativo | `python -m unittest tests.test_auth_regression` | 401 | Critico | integration/docker | automated |
| RBAC-001 | Viewer nao cria asset | Confirmar 403, nao 500 | Usuario viewer | `python -m unittest tests.test_assets_regression` | 403 | Critico | integration/docker | automated |
| USER-001 | Admin cria usuario | Validar criacao | Admin autenticado | `python -m unittest tests.test_assets_regression` | 201 | Alto | integration/docker | automated |
| USER-002 | Lista usuarios | Validar paginacao basica | Usuario criado | `python -m unittest tests.test_assets_regression` | 200 | Medio | integration/docker | automated |
| ASSET-001 | Cria asset | Validar POST asset | Admin autenticado | `python -m unittest tests.test_assets_regression` | 201 | Critico | integration/docker | automated |
| ASSET-002 | Lista ativos | Validar listagem | Asset criado | `python -m unittest tests.test_assets_regression` | 200 | Alto | integration/docker | automated |
| ASSET-003 | Busca hostname | Validar busca operacional | Asset criado | `python -m unittest tests.test_assets_regression` | total >= 1 | Alto | integration/docker | automated |
| ASSET-004 | Busca serial | Validar busca operacional | Asset criado | `python -m unittest tests.test_assets_regression` | total >= 1 | Alto | integration/docker | automated |
| ASSET-005 | Busca patrimonio | Validar busca operacional | Asset criado | `python -m unittest tests.test_assets_regression` | total >= 1 | Alto | integration/docker | automated |
| ASSET-006 | Filtro status | Validar filtro server-side | Asset criado | `python -m unittest tests.test_assets_regression` | total >= 1 | Medio | integration/docker | automated |
| ASSET-007 | Filtro localizacao | Validar filtro server-side | Asset criado | `python -m unittest tests.test_assets_regression` | total >= 1 | Medio | integration/docker | automated |
| ASSET-008 | Asset com usuario | Proteger bug de serializacao | Usuario criado | `python -m unittest tests.test_assets_regression` | 201 e `current_user` serializado | Critico | integration/docker | automated |
| MOVE-001 | Movimentacao cria historico | Validar timeline | Asset em estoque | `python -m unittest tests.test_assets_regression` | 4 movimentos | Critico | integration/docker | automated |
| MOVE-002 | Movimentacao gera auditoria | Validar trilha auditavel | Movimento executado | `python -m unittest tests.test_assets_regression` | Audit contem `MOVE` | Critico | integration/docker | automated |
| MOVE-003 | Dupla submissao | Validar protecao contra duplicidade | Fluxo real com UI | Manual/Playwright futuro | Sem evento duplicado | Alto | e2e/manual | pending |
| IMPORT-001 | CSV valido | Validar staging/aplicacao | Admin autenticado | `python -m unittest tests.test_imports_regression` | 201 e staging 2 | Critico | integration/docker | automated |
| IMPORT-002 | CSV duplicado | Validar conflito | Import valido anterior | `python -m unittest tests.test_imports_regression` | conflito >= 1 | Critico | integration/docker | automated |
| IMPORT-003 | CSV malicioso | Bloquear formula injection | Fixture maliciosa | `python -m unittest tests.test_imports_regression` | validation errors >= 1 | Critico | integration/docker | automated |
| DASH-001 | Dashboard totais | Validar dados agregados | Massa minima | `python -m unittest tests.test_assets_regression` | endpoints 200/coerentes | Alto | integration/docker | automated |
| SIGN-001 | Assinatura API | Gerar HTML | Usuario criado | Validado em suite operacional/script | HTML contem usuario | Alto | integration/docker | automated |
| LEGACY-001 | `/assinaturas/` | Preservar legado publico | App ativo | `python -m unittest tests.test_legacy_routes` | 200 | Critico | smoke/docker | automated |
| LEGACY-002 | `/admin/` | Preservar admin legado | App ativo | `python -m unittest tests.test_legacy_routes` | 200 ou 302 | Critico | smoke/docker | automated |
| SPA-001 | `/` | Carregar SPA | Build presente | `python -m unittest tests.test_legacy_routes` | 200 | Critico | smoke/docker | automated |
| SPA-002 | Deep link | SPA fallback | Build presente | `python -m unittest tests.test_legacy_routes` | 200 | Alto | smoke/docker | automated |
| SPA-003 | `/_assets` | Asset Vite real | Build presente | `python -m unittest tests.test_legacy_routes` | 200 e conteudo | Alto | smoke/docker | automated |
| MIG-001 | Current no head | Validar Alembic | Stack ativo | `python -m unittest tests.test_migrations_regression` | current=head | Critico | docker | automated |
| MIG-002 | Banco limpo aplica migrations | Validar startup limpo | Project isolado | `scripts/ops/validate-operational.ps1 -Cleanup` | App healthy | Critico | docker | automated |
| MIG-003 | Revision id curto | Proteger bug Alembic | Codigo local | `python -m unittest tests.test_operational_contracts` | ids <= 32 | Critico | unit | automated |
| BOOT-001 | Bootstrap cria admin | Validar admin inicial | Banco limpo | `scripts/ops/validate-operational.ps1` | admin criado | Critico | docker | automated |
| BOOT-002 | Bootstrap idempotente | Evitar duplicidade | App restart | Validacao manual/SQL | count admin = 1 | Alto | docker | manual |

## Observacoes

- Testes `integration/docker` usam `OPERATIONAL_BASE_URL` e `ADMIN_PASSWORD`.
- Sem essas variaveis, os testes pulam com mensagem clara.
- `MOVE-003` depende de protecao de dupla submissao em camada UI/API; permanece pendente para automacao dedicada.
