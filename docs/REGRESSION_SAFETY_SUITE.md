# Regression Safety Suite

Data: 2026-06-01

## Objetivo

Proteger os fluxos operacionais criticos do ITAM enterprise sem criar features novas, sem mexer no legado e sem expor segredos.

Esta suite cobre:

- startup Docker
- PostgreSQL e Redis
- migrations Alembic
- bootstrap admin
- auth, refresh e logout
- RBAC basico
- usuarios
- ativos
- movimentacao e historico
- auditoria
- importacao Lansweeper
- dashboard
- assinaturas
- legado `/assinaturas/` e `/admin/`
- SPA fallback e assets Vite

## Politica De Segredos

Nunca grave senha real em:

- `.env.example`
- `docker-compose.yml`
- `README.md`
- `docs/`
- `tests/`
- `scripts/`

Use:

```powershell
$env:ADMIN_EMAIL="estevao.quality@ens.edu.br"
$env:ADMIN_PASSWORD="<DEFINIR_LOCALMENTE>"
$env:ADMIN_NAME="Estevão Ribeiro"
```

`ADMIN_PASSWORD` deve existir apenas em `.env` local nao versionado ou na sessao do terminal.

## Como Rodar Tudo No Windows

```powershell
$env:ADMIN_EMAIL="estevao.quality@ens.edu.br"
$env:ADMIN_PASSWORD="<DEFINIR_LOCALMENTE>"
$env:ADMIN_NAME="Estevão Ribeiro"
.\scripts\ops\validate-operational.ps1
```

Com limpeza do ambiente isolado ao final:

```powershell
.\scripts\ops\validate-operational.ps1 -Cleanup
```

## Como Rodar Manualmente Com Docker

```powershell
$env:ADMIN_EMAIL="estevao.quality@ens.edu.br"
$env:ADMIN_PASSWORD="<DEFINIR_LOCALMENTE>"
$env:ADMIN_NAME="Estevão Ribeiro"
$env:OPERATIONAL_BASE_URL="http://127.0.0.1:8080"
docker compose -p itam_validation up --build -d
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Encerrar:

```powershell
docker compose -p itam_validation down -v --remove-orphans
```

## Testes Criados

- `tests/test_operational_contracts.py`
- `tests/test_auth_regression.py`
- `tests/test_assets_regression.py`
- `tests/test_imports_regression.py`
- `tests/test_legacy_routes.py`
- `tests/test_migrations_regression.py`
- `tests/fixtures/imports/lansweeper_valid.csv`
- `tests/fixtures/imports/lansweeper_duplicate.csv`
- `tests/fixtures/imports/lansweeper_invalid.csv`
- `tests/fixtures/imports/lansweeper_formula_injection.csv`

## Scripts Criados

- `scripts/ops/validate-operational.ps1`
- `scripts/ops/validate-operational.sh`

## Testes Automatizados

- Contratos locais de migrations/routes/requirements.
- Auth: login, login invalido, `/me`, refresh, logout, refresh depois de logout, 401 sem token.
- RBAC: viewer recebe 403 ao criar asset.
- Usuarios: criacao, listagem, busca, update, email invalido.
- Assets: criacao sem usuario, criacao com `current_user_id`, busca, filtros, update, soft delete.
- Movimentacao: historico e auditoria.
- Importacao: CSV valido, duplicado e formula injection.
- Legado: `/assinaturas/` e `/admin/`.
- SPA: fallback e asset Vite.
- Migration: current/head e revision ids curtos.

## Testes Manuais Restantes

- Navegacao real em browser com captura de console.
- Dupla submissao via UI para movimentacao.
- Matriz RBAC completa por endpoint.
- Playwright para login, tabela de ativos, dialog de movimentacao e importacao.

## Troubleshooting

Docker daemon indisponivel:

```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

Porta 8080 ocupada:

- pare o processo local ou ajuste `APP_PORT` e `OPERATIONAL_BASE_URL`.

Senha ausente:

- defina `ADMIN_PASSWORD` na sessao local.
- nao grave a senha em arquivos versionados.

App nao fica healthy:

```powershell
docker compose -p itam_validation logs --tail=200 app
docker compose -p itam_validation ps -a
```

## Bugs Protegidos Por Regressao

- ENUM PostgreSQL duplicado em migration inicial.
- Revision ID Alembic maior que `VARCHAR(32)`.
- Admin default com e-mail rejeitado pelo login.
- Criação de asset com `current_user_id` retornando 500.

## Riscos Restantes

- Testes Docker dependem de Docker Desktop ativo.
- Suite HTTP usa massa incremental; recomenda-se `-Cleanup` para validacao limpa.
- Frontend ainda nao possui Vitest/Testing Library configurado. O build TypeScript/Vite cobre regressao de compilacao; testes de componente ficam como proximo passo.
