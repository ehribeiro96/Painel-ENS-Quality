# HISTORY-H1 — Readability and Traceability Report

## Status

`GO_HISTORY_READABILITY_IMPROVED`

`GO_HISTORY_BACKEND_ENRICHED`

`PARTIAL_AUDIT_TRACE_REMAINS_FUTURE`

`PARTIAL_AUTH_CREDENTIAL_MISSING`

`PARTIAL_RUNTIME_BLOCKED`

Audit run: 2026-06-21T16:17:51-03:00.

## Problema

O histórico do ativo já existia em:

```text
GET /api/v1/assets/{asset_id}/history
```

Antes do patch, a resposta do endpoint era baseada em `AssetMovement` e expunha principalmente IDs técnicos:

```text
asset_id
previous_user_id
new_user_id
responsible_id
```

No frontend, a timeline do detalhe do ativo usava esses IDs truncados como informação principal. Para operação N2 isso reduzia a legibilidade para responder rapidamente:

- quem movimentou;
- qual ativo foi movimentado;
- de qual usuário/local/status saiu;
- para qual usuário/local/status foi;
- se houve macro vinculada à movimentação;
- se a macro vinculada foi copiada.

## Estratégia escolhida

`STRATEGY_BACKEND_HISTORY_ENRICHMENT` com renderização mínima no frontend.

Motivo:

- o backend já tinha os relacionamentos necessários sem migration;
- `AssetMovement` já guarda os IDs de usuário, responsável, status e local;
- `MacroGeneration` já vincula macro ao movimento por `context_type="asset_movement"` e `context_id=movement_id`;
- o frontend precisava trocar IDs como texto principal por labels humanas quando disponíveis;
- filtros/correlação avançada em `/audit-logs` virariam feature maior e ficaram para `AUDIT-H1`.

## Correção aplicada

### Backend

Endpoint afetado:

```text
GET /api/v1/assets/{asset_id}/history
```

O DTO `MovementRead` foi enriquecido com campos opcionais, preservando todos os campos existentes:

```text
previous_user_name
new_user_name
responsible_name
asset_label
macro_generation_id
macro_copied
macro_copied_at
```

Campos antigos preservados:

```text
id
asset_id
previous_user_id
new_user_id
previous_status
new_status
previous_location
new_location
responsible_id
justification
notes
created_at
```

Não houve migration.
Não houve alteração no modelo `AssetMovement`.
Não houve alteração em `MacroService.generate_for_movement`.
Não houve alteração em `MoveAssetDialog`.

### Frontend

A timeline em `AssetDetailsPage` agora:

- exibe nome do responsável quando disponível;
- exibe nome do usuário anterior/novo quando disponível;
- usa fallback claro para campos ausentes;
- mantém ID curto apenas como detalhe secundário;
- exibe label do ativo quando disponível;
- exibe rastreio de macro vinculada e estado de cópia.

## Campos antes/depois

Antes:

```text
Responsável: ID curto
Antes: STATUS | local | ID curto ou sem usuário
Depois: STATUS | local | ID curto ou sem usuário
Macro: não visível no histórico do ativo
```

Depois:

```text
Responsável: Nome · ID curto
Ativo: hostname/patrimônio/serial disponível
Antes: STATUS | origem | Nome do usuário · ID curto
Depois: STATUS | destino | Nome do usuário · ID curto
Macro <id curto> · copiada/não copiada
```

Fallbacks usados:

```text
Responsável não informado
Usuário não informado
Origem não informada
Destino não informado
Macro não vinculada
Status não informado
```

## O que ficou fora do escopo

- filtros avançados de audit logs;
- nova tela de auditoria correlacionada;
- migration ou nova tabela;
- alteração de auth/RBAC;
- alteração de Dashboard H2;
- alteração de Users H1;
- alteração de Docker/Compose;
- alteração de IA/Ollama;
- alteração de package files;
- alteração de importação Lansweeper;
- redesign visual amplo.

## Testes

Backend:

```text
source .venv/bin/activate
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests
```

Resultado fresco após o patch:

```text
Ran 153 tests in 0.322s
OK (skipped=8)
```

Frontend:

```text
node -p "process.platform + ' ' + process.arch + ' ' + process.execPath"
linux x64 /home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin/node

npm -v
10.9.8

npm run build
✓ built in 1.82s
```

`npm run typecheck --if-present`, `npm run lint --if-present` e `npm run test --if-present` não reportaram falha no ambiente atual.

Package files:

```text
frontend/itam-platform/package.json: sem diff
frontend/itam-platform/package-lock.json: sem diff
```

## UAT

UAT autenticado completo ficou parcial nesta execução:

```text
/tmp/painel_auth_uat_h2_credentials.txt: ausente
127.0.0.1:8000: fechado
127.0.0.1:8080: fechado
127.0.0.1:5173: fechado
127.0.0.1:5174: fechado
```

Foi tentado subir runtime local seguro:

- `docker compose start postgres redis` iniciou os containers e `docker compose ps` mostrou `postgres` e `redis` como `healthy`;
- `uvicorn app.main:app --host 127.0.0.1 --port 8000` foi iniciado em background;
- a checagem de `/health/ready` não ficou pronta dentro do timeout;
- conexões TCP para as portas expostas `5432`, `6379` e `8000` não responderam no ambiente WSL atual;
- o processo temporário `uvicorn` foi encerrado;
- não foi impresso segredo, token, cookie ou Authorization header.

Classificação runtime:

```text
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

## Riscos restantes

- A validação UAT HTTP autenticada ficou bloqueada por credencial UAT ausente e indisponibilidade de portas/runtime no ambiente atual.
- A correlação de auditoria ainda depende da tela genérica `/audit-logs`; filtros por entidade/ação/período continuam para próxima boundary.
- Quando não há macro gerada para um movimento, o histórico exibe `Macro não vinculada`, que é correto, mas ainda exige investigação manual se a operação esperava macro.
- A resposta do endpoint foi enriquecida com campos opcionais; consumidores antigos continuam compatíveis porque os campos anteriores foram preservados.

## Próxima boundary

`AUDIT-H1 — improve audit log filters and entity traceability`
