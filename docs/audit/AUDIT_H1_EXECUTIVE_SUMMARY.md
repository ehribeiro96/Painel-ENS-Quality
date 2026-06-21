# AUDIT-H1 — Executive Summary

## Status final

```text
GO_AUDIT_FILTERS_TRACEABILITY_IMPROVED
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

Audit run: 2026-06-21T16:27:19-03:00.

## Escopo

Melhorar a rastreabilidade dos logs de auditoria para operação N2, usando campos existentes e sem reabrir History-H1.

## Diagnóstico

O endpoint `/api/v1/audit-logs` existia e retornava campos úteis, mas não aceitava filtros. A UI exibia apenas chips “em breve”, sem permitir investigação por entidade, ação, período ou request/correlation.

Campos existentes no modelo `AuditLog` usados nesta boundary:

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

## Estratégia

```text
STRATEGY_BACKEND_AND_FRONTEND_FILTERS
```

## Correção aplicada

Backend:

- `GET /api/v1/audit-logs` recebeu filtros opcionais.
- paginação existente foi preservada.
- endpoint sem filtros continua compatível.
- nenhuma migration foi criada.

Frontend:

- `AuditLogsPage` agora tem formulário de filtros.
- `api.audit()` aceita query string opcional.
- a tabela mostra request/correlation id curto.
- detalhes técnicos são expansíveis e têm redaction óbvia de chaves/valores sensíveis.

## Filtros implementados

```text
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

## Validações

Backend:

```text
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests
Ran 157 tests
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

UAT autenticado completo ficou bloqueado:

```text
/tmp/painel_auth_uat_h2_credentials.txt ausente
127.0.0.1:8000/8080/5173/5174 fechados
```

## Segurança e escopo

- Nenhuma credencial foi impressa.
- Nenhum token/cookie/storage state foi salvo ou commitado.
- Nenhuma migration foi criada.
- Nenhum reset de banco foi executado.
- Nenhuma alteração em Docker/Compose.
- Nenhuma alteração em package files.
- Nenhuma alteração em auth/RBAC.
- Nenhuma alteração em Dashboard H2.
- Nenhuma alteração em Users H1.
- Nenhuma alteração em History-H1.
- Nenhuma alteração em MoveAssetDialog.
- Nenhuma alteração em IA/Ollama.
- Nenhuma alteração em ImportService.

## Riscos remanescentes

- UAT real ainda precisa de runtime e credencial local.
- `actor_id` continua como ID no endpoint; nome do usuário não foi enriquecido nesta boundary para evitar mudança de contrato maior.
- Busca em payload JSON não foi implementada.
- Docker build/apt-get continua pendência separada.

## Próxima boundary recomendada

```text
RUNTIME-H1 — restore local UAT runtime and credentials
```

Se runtime já estiver resolvido por fora, seguir para:

```text
RELEASE-H1 — production readiness and final UAT checklist
```
