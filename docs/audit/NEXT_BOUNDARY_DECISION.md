# Next Boundary Decision

Boundary atual: `HISTORY-H1 — improve asset history readability and audit traceability`.

## Estado consolidado

- `FRONTEND-AUTH-FREEZE-H2`: concluída; commit `0e70dd1 fix(frontend): handle dashboard status response shape`.
- `USERS-API-H1`: concluída; commit `6c18975 fix(users): serialize legacy email values`.
- `HISTORY-H1`: patch aplicado para melhorar legibilidade do histórico do ativo e enriquecer o DTO de histórico com labels humanas e rastreio de macro/cópia.

## Status HISTORY-H1

```text
GO_HISTORY_READABILITY_IMPROVED
GO_HISTORY_BACKEND_ENRICHED
PARTIAL_AUDIT_TRACE_REMAINS_FUTURE
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

## Decisão objetiva

A próxima boundary deve focar auditoria, não histórico do ativo.

Motivo:

- `GET /api/v1/assets/{asset_id}/history` já existe.
- O endpoint foi enriquecido sem migration e preservando campos antigos.
- A UI de detalhe do ativo passou a priorizar labels humanas e usar IDs apenas como detalhe secundário.
- A auditoria ainda é genérica e carece de filtros/correlação mais úteis para prova operacional diária.
- UAT autenticado completo precisa de desbloqueio operacional separado se a credencial UAT `/tmp/painel_auth_uat_h2_credentials.txt` não estiver disponível ou se o runtime local não expuser portas HTTP.

## Evidência resumida HISTORY-H1

Campos opcionais adicionados a `MovementRead`:

```text
previous_user_name
new_user_name
responsible_name
asset_label
macro_generation_id
macro_copied
macro_copied_at
```

Validações executadas:

```text
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests -> OK (153 tests, skipped=8)
npm run build -> OK
```

Limitação UAT:

```text
/tmp/painel_auth_uat_h2_credentials.txt ausente
127.0.0.1:8000/8080/5173/5174 fechados no início
postgres/redis iniciados e healthy no docker compose ps
uvicorn temporário não expôs /health/ready dentro do timeout
```

## Próxima boundary recomendada

1. `AUDIT-H1 — improve audit log filters and entity traceability`
   - Objetivo: melhorar investigação operacional em `/audit-logs` com filtros pequenos e úteis.
   - Escopo sugerido:
     - filtro por entidade;
     - filtro por ação;
     - busca por `entity_id`/correlation quando disponível;
     - preservação de payload técnico sem expor segredo;
     - documentação de limites da auditoria.
   - Critério de GO:
     - `/audit-logs` permite localizar eventos de `Asset`, `AssetMovement` e `MacroGeneration` do fluxo sintético;
     - sem alteração de auth/RBAC;
     - sem migration, salvo justificativa explícita em boundary própria;
     - testes/backend/frontend passam conforme aplicável.

## Boundary de desbloqueio condicional

Se for obrigatório validar UAT autenticado antes de `AUDIT-H1`, usar:

```text
RUNTIME-UAT-H1 — restore local authenticated runtime smoke path
```

Escopo limitado:

- recriar/fornecer credencial UAT segura em `/tmp` sem versionar segredo;
- validar exposição local de portas no WSL/Docker;
- confirmar `/`, `/api/v1/users?page_size=100`, `/api/v1/assets`, `/api/v1/assets/{id}/history` e `/api/v1/audit-logs`;
- não alterar produto salvo se houver causa raiz comprovada.

## Boundaries condicionais futuras

2. `HISTORY-H2 — enrich backend asset history DTO`
   - Condição: somente se forem necessários campos adicionais além dos opcionais criados em HISTORY-H1.
   - Evitar se `AUDIT-H1` resolver a rastreabilidade restante.

3. `MACRO-H2 — strengthen macro copy audit UX`
   - Condição: se operadores precisarem de feedback visual/auditável mais forte sobre `copied=true` fora do detalhe do ativo.

## O que não fazer agora

- Não reabrir `FRONTEND-AUTH-FREEZE-H2`.
- Não reabrir `USERS-API-H1`.
- Não alterar usuário UAT H2.
- Não imprimir credenciais, tokens, cookies ou storage state.
- Não apagar dados locais nem resetar banco.
- Não alterar `.env`, `.env.*`, Docker/Compose, migrations, package files, assets, CI ou IA/Ollama.
- Não refatorar todo o audit log junto com histórico.

## Decisão final

Próxima boundary recomendada: `AUDIT-H1 — improve audit log filters and entity traceability`.
