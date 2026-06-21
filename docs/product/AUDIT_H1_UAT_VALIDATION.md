# AUDIT-H1 — UAT Validation

## Status

```text
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

Audit run: 2026-06-21T16:27:19-03:00.

## Credencial UAT

A credencial local esperada não estava disponível em:

```text
/tmp/painel_auth_uat_h2_credentials.txt
```

A boundary não imprimiu senha, token, cookie, Authorization header ou storage state.

## Estado de runtime local

Checagem inicial de portas:

```text
127.0.0.1:8000 fechado
127.0.0.1:8080 fechado
127.0.0.1:5173 fechado
127.0.0.1:5174 fechado
```

Conforme boundary, não foi reaberto o problema de Docker/apt-get e não foi feita correção de infraestrutura.

## Alvos UAT solicitados

Não foi possível validar via HTTP/browser autenticado nesta execução:

```text
GET /api/v1/audit-logs
GET /api/v1/audit-logs?page_size=20
GET /api/v1/audit-logs?action=<ação_existente>
GET /api/v1/audit-logs?entity_type=<tipo_existente>
GET /api/v1/audit-logs?correlation_id=<id_existente>
/
/assets
/api/v1/users?page_size=100
/api/v1/assets/{id}/history
```

Motivo:

```text
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

## Validação substituta executada

Foram executados testes e build locais:

```text
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests
Ran 157 tests in 0.260s
OK (skipped=8)

npm run build
✓ built in 1.70s
```

## Cobertura funcional por teste

Foi adicionado teste unitário para validar que os filtros de auditoria usam colunas existentes, sem migration:

```text
actor_id
action
entity
entity_id
request_id
correlation_id
source
created_at
```

Também foi validado que o helper aceita ausência de filtros, preservando a listagem padrão sem filtro.

## Resultado operacional esperado

Quando runtime e autenticação estiverem disponíveis, `/audit-logs` deve permitir:

- lista sem filtros;
- filtro por ação;
- filtro por entidade;
- busca por texto/ID/correlação/request;
- filtro por fonte;
- filtro por período;
- limpar filtros.

## Achados secundários

- A validação UAT precisa de uma boundary operacional específica para restaurar credencial local e runtime HTTP.
- A melhoria de Docker build/apt-get continua separada e não foi tocada por AUDIT-H1.
