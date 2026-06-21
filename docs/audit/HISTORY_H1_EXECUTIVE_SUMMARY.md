# HISTORY-H1 — Executive Summary

## Status final

```text
GO_HISTORY_READABILITY_IMPROVED
GO_HISTORY_BACKEND_ENRICHED
PARTIAL_AUDIT_TRACE_REMAINS_FUTURE
PARTIAL_AUTH_CREDENTIAL_MISSING
PARTIAL_RUNTIME_BLOCKED
```

Audit run: 2026-06-21T16:17:51-03:00.

## Escopo

Melhorar a legibilidade do histórico do ativo e a rastreabilidade operacional do fluxo:

```text
Ativo -> Movimentação -> Macro -> Cópia -> Auditoria
```

sem refatoração ampla, sem migration e sem reabrir Dashboard H2 ou Users H1.

## Diagnóstico

O endpoint `GET /api/v1/assets/{asset_id}/history` já existia, mas retornava principalmente IDs de relacionamento. O frontend exibia esses IDs truncados como texto principal.

Classificação inicial:

```text
HISTORY_IDS_ONLY
HISTORY_MISSING_MACRO_TRACE
HISTORY_ENDPOINT_OK_UI_WEAK
HISTORY_BACKEND_NEEDS_ENRICHMENT
```

## Estratégia

```text
STRATEGY_BACKEND_HISTORY_ENRICHMENT
```

com ajuste mínimo de renderização no frontend.

## Correção aplicada

Backend:

- `MovementRead` recebeu campos opcionais de leitura:
  - `previous_user_name`
  - `new_user_name`
  - `responsible_name`
  - `asset_label`
  - `macro_generation_id`
  - `macro_copied`
  - `macro_copied_at`
- `GET /api/v1/assets/{asset_id}/history` enriquece a resposta com nomes de usuários, label do ativo e macro vinculada por `context_type="asset_movement"`.

Frontend:

- `AssetDetailsPage` exibe nomes quando disponíveis.
- IDs curtos ficam como detalhe secundário.
- Fallbacks claros substituem valores ausentes.
- Timeline mostra se há macro vinculada e se foi copiada.

Testes:

- teste operacional de histórico foi ajustado para verificar novos campos quando o ambiente operacional estiver disponível;
- teste unitário de contrato valida que `MovementRead` aceita os campos opcionais;
- `Movement` TypeScript foi atualizado com os campos opcionais.

## Validações

Backend:

```text
python -m compileall -q backend/app backend/alembic tests
python -m unittest discover -s tests
Ran 153 tests
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

Package files:

```text
frontend/itam-platform/package.json: sem diff
frontend/itam-platform/package-lock.json: sem diff
```

Runtime/UAT:

```text
/tmp/painel_auth_uat_h2_credentials.txt ausente
127.0.0.1:8000 fechado no início
127.0.0.1:8080 fechado no início
postgres/redis iniciados e healthy no docker compose ps
uvicorn temporário não expôs /health/ready dentro do timeout
processo uvicorn temporário encerrado
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
- Nenhuma alteração em `MoveAssetDialog`.
- Nenhuma alteração em `MacroService.generate_for_movement`.

## Risco remanescente

A auditoria ainda precisa de uma boundary própria para filtros e correlação visual por entidade/ação/período. HISTORY-H1 enriqueceu o histórico do ativo, mas não transformou `/audit-logs` em ferramenta avançada de investigação.

UAT autenticado completo ficou bloqueado por credencial UAT ausente e indisponibilidade do runtime HTTP no ambiente atual.

## Próxima boundary recomendada

```text
AUDIT-H1 — improve audit log filters and entity traceability
```
