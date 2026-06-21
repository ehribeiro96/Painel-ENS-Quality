# Next Boundary Decision

Boundary atual: `AUDIT-H1 — improve audit log filters and entity traceability`.

## Estado consolidado

- `FRONTEND-AUTH-FREEZE-H2`: concluída; commit `0e70dd1 fix(frontend): handle dashboard status response shape`.
- `USERS-API-H1`: concluída; commit `6c18975 fix(users): serialize legacy email values`.
- `HISTORY-H1`: concluída; commit `1cce914 feat(history): enrich asset history traceability`.
- `AUDIT-H1`: filtros de auditoria implementados no backend e expostos no frontend, com UAT autenticado bloqueado por ambiente/credencial.

## Status AUDIT-H1

```text
GO_AUDIT_FILTERS_TRACEABILITY_IMPROVED
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

## Decisão objetiva

A próxima boundary deve desbloquear runtime/UAT antes de avançar para release final.

Motivo:

- `/api/v1/audit-logs` agora aceita filtros úteis usando campos existentes.
- `AuditLogsPage` agora expõe filtros por ação, entidade, fonte, texto/ID/correlação e período.
- Testes backend e build frontend passaram.
- UAT autenticado real ainda não pôde ser executado porque a credencial `/tmp/painel_auth_uat_h2_credentials.txt` está ausente e as portas locais de runtime estavam fechadas.

## Evidência resumida AUDIT-H1

Filtros implementados:

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

Campos usados sem migration:

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

Validações executadas:

```text
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests -> OK (157 tests, skipped=8)
npm run build -> OK
```

Limitação UAT:

```text
/tmp/painel_auth_uat_h2_credentials.txt ausente
127.0.0.1:8000 fechado
127.0.0.1:8080 fechado
127.0.0.1:5173 fechado
127.0.0.1:5174 fechado
```

## Próxima boundary recomendada

1. `RUNTIME-H1 — restore local UAT runtime and credentials`
   - Objetivo: restaurar caminho de smoke autenticado local sem mexer em produto sem causa raiz comprovada.
   - Escopo sugerido:
     - recriar/fornecer credencial UAT segura em `/tmp` sem versionar segredo;
     - validar exposição HTTP local;
     - confirmar `/`, `/assets`, `/api/v1/users?page_size=100`, `/api/v1/assets/{id}/history` e `/api/v1/audit-logs`;
     - validar filtros AUDIT-H1 por ação/entidade/search/período;
     - não alterar Docker/Compose salvo boundary explícita.

## Boundary seguinte após runtime

2. `RELEASE-H1 — production readiness and final UAT checklist`
   - Condição: runtime/UAT local autenticado disponível e smoke crítico aprovado.
   - Objetivo: checklist final para release/piloto controlado.

## Pendência operacional separada

```text
OPS-DOCKER-H1 — resolve Docker build apt-get timeout
```

Registrar separadamente se Docker build voltar a ser prioridade. Não misturar com filtros de auditoria.

## Boundaries condicionais futuras

3. `AUDIT-H2 — complete audit traceability filters`
   - Condição: somente se operação N2 precisar de busca em payload JSON, nomes de usuário enriquecidos ou filtros avançados além do patch AUDIT-H1.

4. `AUDIT-UX-H2 — improve audit investigation ergonomics`
   - Condição: somente após validação UAT dos filtros atuais, caso operadores peçam melhorias visuais adicionais.

## O que não fazer agora

- Não reabrir `HISTORY-H1`.
- Não reabrir `FRONTEND-AUTH-FREEZE-H2`.
- Não reabrir `USERS-API-H1`.
- Não alterar usuário UAT sem boundary runtime/autorização.
- Não imprimir credenciais, tokens, cookies ou storage state.
- Não apagar dados locais nem resetar banco.
- Não alterar `.env`, `.env.*`, Docker/Compose, migrations, package files, assets, CI ou IA/Ollama.
- Não transformar auditoria em módulo de relatórios/exportação nesta etapa.

## Decisão final

Próxima boundary recomendada: `RUNTIME-H1 — restore local UAT runtime and credentials`.
