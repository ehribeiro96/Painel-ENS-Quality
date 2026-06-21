# AUDIT-H1 — Filters and Traceability Report

## Status

```text
GO_AUDIT_FILTERS_TRACEABILITY_IMPROVED
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

Audit run: 2026-06-21T16:27:19-03:00.

## Problema

`GET /api/v1/audit-logs` retornava página de logs de auditoria, mas sem filtros. A tela `AuditLogsPage` também mostrava chips estáticos de “em breve”, então operação N2 precisava rastrear manualmente eventos por ação, entidade, IDs de entidade, usuário, fonte, request/correlation e período.

Classificação inicial:

```text
AUDIT_ENDPOINT_NO_FILTERS
AUDIT_UI_NO_FILTERS
AUDIT_UI_WEAK_TRACEABILITY
```

## Estratégia escolhida

```text
STRATEGY_BACKEND_AND_FRONTEND_FILTERS
```

Motivo:

- o modelo `AuditLog` já possui campos filtráveis;
- os campos já têm índices relevantes no modelo/migrations existentes;
- não foi necessária migration;
- o endpoint sem filtros pôde ser preservado;
- a UI podia expor filtros simples sem redesign amplo.

## Correção aplicada

### Backend

Arquivo:

```text
backend/app/api/v1/routes/audit.py
```

`GET /api/v1/audit-logs` agora aceita filtros opcionais e preserva paginação:

```text
page
page_size
entity_type
entity_id
action
user_id
source
correlation_id
request_id
date_from
date_to
search
```

Observação de contrato:

- `entity_type` filtra a coluna existente `AuditLog.entity`.
- `user_id` filtra a coluna existente `AuditLog.actor_id`.
- `search` é busca auxiliar textual para operação: entidade, fonte, request/correlation e IDs convertidos para texto.
- `action` usa o enum existente `AuditAction`.
- filtros inválidos de UUID/enum/data seguem validação FastAPI/Pydantic e não geram 500.

### Frontend

Arquivos:

```text
frontend/itam-platform/src/lib/api.ts
frontend/itam-platform/src/pages/AuditLogsPage.tsx
```

A tela agora permite:

- filtrar por ação;
- filtrar por entidade;
- filtrar por fonte;
- buscar por texto/ID/correlação/request;
- filtrar por data inicial e final;
- limpar filtros.

A tabela agora exibe:

- ação;
- entidade;
- descrição com ID de entidade curto;
- usuário/ator com fallback;
- fonte;
- request id curto;
- correlation id curto;
- detalhes técnicos redigidos para chaves sensíveis óbvias.

## Filtros implementados

```text
entity_type -> AuditLog.entity
entity_id -> AuditLog.entity_id
action -> AuditLog.action
user_id -> AuditLog.actor_id
source -> AuditLog.source
correlation_id -> AuditLog.correlation_id
request_id -> AuditLog.request_id
date_from -> AuditLog.created_at >= date_from
date_to -> AuditLog.created_at <= date_to
search -> entity/source/request_id/correlation_id/entity_id/actor_id
```

## Campos exibidos

```text
created_at
action
entity
entity_id
actor_id
source
request_id
correlation_id
before/after redigidos em detalhes expansíveis
```

Fallbacks:

```text
Ação não informada
Entidade não informada
Usuário não informado
Fonte não informada
Correlação não informada
Sem detalhe técnico
```

## O que ficou fora do escopo

- migration;
- nova tabela;
- exportação CSV;
- dashboard de auditoria;
- alteração de auth/RBAC;
- alteração de History-H1;
- alteração de MoveAssetDialog;
- alteração de Docker/Compose/apt-get;
- alteração de IA/Ollama;
- alteração de ImportService;
- mascaramento profundo de todos os payloads históricos além de redaction óbvia por chave/valor.

## Testes

Backend:

```text
source .venv/bin/activate
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests
```

Resultado:

```text
Ran 157 tests in 0.260s
OK (skipped=8)
```

Frontend:

```text
node -p "process.platform + ' ' + process.arch + ' ' + process.execPath"
linux x64 /home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin/node

npm -v
10.9.8

npm run build
✓ built in 1.70s
```

Package files:

```text
frontend/itam-platform/package.json: sem diff
frontend/itam-platform/package-lock.json: sem diff
```

## UAT

UAT HTTP/browser autenticado ficou bloqueado nesta execução:

```text
/tmp/painel_auth_uat_h2_credentials.txt: ausente
127.0.0.1:8000: fechado
127.0.0.1:8080: fechado
127.0.0.1:5173: fechado
127.0.0.1:5174: fechado
```

Classificação:

```text
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

Nenhum token, cookie, senha, Authorization header ou storage state foi impresso.

## Riscos restantes

- Validação UAT autenticada real ainda depende de restaurar credencial/runtime local.
- A coluna `actor_id` ainda não é enriquecida com nome do usuário na resposta; a UI exibe ID curto com fallback.
- `search` é uma busca operacional simples; filtros avançados full-text ou por payload JSON ficaram fora do escopo.
- Payloads `before/after` são exibidos em detalhes expansíveis com redaction óbvia, mas auditoria histórica ainda deve evitar registrar segredo na origem.

## Próxima boundary

Como os filtros foram implementados e testados, mas runtime/UAT segue bloqueado, a próxima boundary recomendada é:

```text
RUNTIME-H1 — restore local UAT runtime and credentials
```

Pendência separada, se priorizada pela operação:

```text
OPS-DOCKER-H1 — resolve Docker build apt-get timeout
```
