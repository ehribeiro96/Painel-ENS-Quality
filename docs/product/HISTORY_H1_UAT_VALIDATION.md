# HISTORY-H1 — UAT Validation

## Status

```text
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

Audit run: 2026-06-21T16:17:51-03:00.

## Credencial UAT

A credencial local esperada da boundary AUTH-UAT-H2 não estava disponível em:

```text
/tmp/painel_auth_uat_h2_credentials.txt
```

Nenhuma senha, token, cookie, storage state ou Authorization header foi impresso.

## Runtime

Estado inicial de portas:

```text
127.0.0.1:8000 fechado
127.0.0.1:8080 fechado
127.0.0.1:5173 fechado
127.0.0.1:5174 fechado
```

Foi feita tentativa conservadora de runtime local:

```text
docker compose start postgres redis
PYTHONPATH=backend python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Resultado:

```text
postgres: healthy no docker compose ps
redis: healthy no docker compose ps
GET /health/ready: não ficou pronto dentro do timeout
TCP 127.0.0.1:5432: sem resposta no ambiente atual
TCP 127.0.0.1:6379: sem resposta no ambiente atual
TCP 127.0.0.1:8000: sem resposta no ambiente atual
```

O processo temporário `uvicorn` foi encerrado após o bloqueio.

## Rotas alvo

Não foi possível executar UAT HTTP autenticado fresco para as rotas abaixo nesta execução:

```text
POST /api/v1/auth/login
GET /api/v1/users?page_size=100
GET /api/v1/assets
GET /api/v1/assets/{id}/history
GET /api/v1/audit-logs
```

Motivo:

```text
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

## Validação substituta executada

Foram executadas validações automatizadas locais sem imprimir segredo:

```text
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests
Ran 153 tests in 0.322s
OK (skipped=8)

npm run build
✓ built in 1.82s
```

Também foi mantido teste de contrato para `MovementRead` aceitar os campos opcionais de rastreabilidade do histórico:

```text
previous_user_name
new_user_name
responsible_name
asset_label
macro_generation_id
macro_copied
macro_copied_at
```

## Resultado do histórico esperado pelo patch

Após o patch, `GET /api/v1/assets/{id}/history` preserva campos antigos e tenta retornar campos opcionais enriquecidos:

```text
asset_label
previous_user_name
new_user_name
responsible_name
macro_generation_id
macro_copied
macro_copied_at
```

A UI usa labels humanas quando disponíveis e mantém IDs curtos apenas como detalhe secundário.

## Auditoria

A boundary não implementou filtros avançados em `/audit-logs`. A auditoria genérica permanece como fonte técnica, e a melhoria de filtros/correlação fica para `AUDIT-H1`.

## Achados secundários

- Runtime local via Docker/WSL precisa ser desbloqueado antes de uma validação UAT autenticada completa.
- A credencial UAT H2 em `/tmp` precisa ser recriada ou fornecida para smoke autenticado sem expor segredo.
