# Project Hygiene Remediation Plan

Data: 2026-06-02

## Escopo

Rodada conservadora de saneamento para reduzir risco operacional sem criar
features novas, sem remover o legado de assinaturas e sem alterar a arquitetura
ativa do ENS ITAM Platform.

## Inventario e classificacao

| Caminho | Classificacao | Motivo | Acao | Risco | Validacao |
|---|---|---|---|---|---|
| `backend/app` | ACTIVE_RUNTIME | Backend FastAPI modular ativo | Manter | Alto se alterado | compileall, unittest |
| `backend/alembic` | ACTIVE_RUNTIME | Migrations PostgreSQL | Manter | Alto se alterado | alembic/compileall |
| `frontend/itam-platform` | ACTIVE_RUNTIME | SPA React + Vite ativa | Manter | Alto se alterado | npm run build |
| `run.py` | ACTIVE_RUNTIME | Entrypoint oficial | Manter | Alto se alterado | import/startup |
| `docker-compose.yml` | ACTIVE_RUNTIME | Runtime oficial postgres/redis/app | Manter | Alto se alterado | docker compose config |
| `backend/Dockerfile` | ACTIVE_RUNTIME | Build oficial app integrado | Manter | Alto se alterado | docker build/config |
| `src/legacy` | LEGACY_SUPPORTED | Rotas `/assinaturas/` e `/admin/` | Manter e endurecer defaults | Medio | smoke legacy |
| `assets/templates`, `assets/static` | LEGACY_SUPPORTED | Templates e assets de assinatura | Manter | Alto se removido | smoke legacy |
| `frontend/app` | ARCHIVE_CANDIDATE | Frontend antigo fora do runtime ativo | Movido para quarentena | Baixo | npm build ativo |
| `frontend/legacy/Base44` | ARCHIVE_CANDIDATE | Prototipo com imports quebrados | Movido para quarentena | Baixo | npm build ativo |
| `infra/nginx/nginx.conf` | KEEP_FOR_NOW | Proxy opcional | Atualizado para `app:8080` | Baixo | revisao config |
| `.env` | SENSITIVE_REMOVE | Config local sensivel | Mantido local e ignorado; nao distribuir | Alto se versionado | gitignore/dockerignore |
| `secrets/` | SENSITIVE_REMOVE | Segredos locais | Ignorado; script gera placeholders | Alto se versionado | gitignore/dockerignore |
| `.venv`, `node_modules`, `dist`, caches | DELETE_SAFE | Artefatos regeneraveis | Ignorar; nao incluir em bundle | Baixo | gitignore/dockerignore |
| `backups`, `uat_evidence` | SENSITIVE_REMOVE | Evidencias/backups locais | Ignorar; nao incluir em bundle | Alto se versionado | gitignore/dockerignore |

## Correcoes priorizadas

- Sanitizacao de `.env.example`.
- Remocao de defaults sensiveis no legado Flask.
- Tratamento central de `IntegrityError` como HTTP 409.
- Filtro operacional `without_user=true` para o card "Sem usuario".
- Apply parcial de importacao com savepoint por linha.
- Declaracao direta de `starlette`.
- Arquivamento conservador de prototipos frontend quebrados.
- Atualizacao de NGINX opcional para arquitetura integrada.
- Tooling minimo: `pyproject.toml`, `.editorconfig`, workflow de qualidade.

## Itens preservados

- Legado `/assinaturas/` e `/admin/`.
- Migrations existentes.
- Pipeline de importacao Lansweeper por planilha.
- Scripts operacionais UAT/backup/restore.
- `.env` local do operador, sem revelar valores.

## Riscos restantes

- Arquivos locais ignorados ainda existem no workspace e nao devem ser
  empacotados manualmente.
- Legado Flask continua grande e deve ser modularizado em fase dedicada.
- `src/legacy` ainda depende de variaveis de ambiente para fluxos Graph/SMTP.

## Referencia visual

- Prints enviados pelo usuario: UX_REFERENCE_FROM_PRINTS.
- frontend/legacy/Base44: ARCHIVE_CANDIDATE, nao confirmado como origem dos prints.
- frontend/itam-platform: ACTIVE_RUNTIME para aplicacao de UX.

