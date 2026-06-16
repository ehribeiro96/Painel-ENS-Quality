# CI-H3 — Workflow Final Review

Boundary: `CI-H3 — harden docker build workflow as manual-only, no publish`

## Checklist final

| Item | Resultado |
|---|---|
| Workflow existe em `.github/workflows/docker-build-push.yml` | sim |
| Workflow será versionado nesta boundary | sim |
| Trigger automático `push` removido | sim |
| `workflow_dispatch` mantido como único trigger | sim |
| `pull_request_target` ausente | sim |
| `schedule` ausente | sim |
| `workflow_run` ausente | sim |
| `permissions: contents: read` | sim |
| `packages: write` removido | sim |
| `docker/login-action` removido | sim |
| GHCR removido | sim |
| `latest` removido | sim |
| `docker/build-push-action@v5` mantido como build-only | sim |
| `push: false` configurado | sim |
| `file: backend/Dockerfile` configurado | sim |
| `context: .` mantido | sim |
| Secret do GitHub Actions não usado pelo workflow final | sim |
| Publish executado nesta boundary | não |
| Push remoto executado nesta boundary | não |
| Tag de release criada | não |
| Dockerfile alterado | não |
| docker-compose alterado | não |
| Código funcional alterado | não |

## Forbidden patterns

Padrões proibidos verificados contra o workflow final:

- `pull_request_target`
- `workflow_run`
- `schedule:`
- `packages: write`
- `docker/login-action`
- `push: true`
- `ghcr.io`
- `:latest`
- `secrets.`
- `GITHUB_TOKEN`
- `docker push`
- `docker login`

Resultado: não encontrados no workflow final.

## Required patterns

Padrões obrigatórios verificados contra o workflow final:

- `workflow_dispatch`
- `contents: read`
- `docker/setup-buildx-action`
- `docker/build-push-action`
- `push: false`
- `file: backend/Dockerfile`
- `context: .`

Resultado: encontrados no workflow final.

## Revisão do Dockerfile path

Leitura estática confirmou que o Dockerfile real está em `backend/Dockerfile` e usa cópias relativas a partir da raiz do repositório, incluindo:

- `frontend/itam-platform`
- `backend/requirements.txt`
- `requirements-legacy.txt`
- `backend`
- `src`
- `assets`
- `run.py`

Decisão: manter `context: .` e definir explicitamente `file: backend/Dockerfile`.

## actionlint

Resultado: `actionlint not installed; skipping`.

Classificação: ressalva operacional, sem instalação feita.

## Scanner redigido

O scanner de termos sensíveis foi executado somente nos arquivos allowlisted CI-H3.

Classificação esperada:

- Termos como `secret`, `token`, `password`, `GITHUB_TOKEN`, `GHCR` ou nomes equivalentes podem aparecer em contexto documental/negativo nos relatórios e índices.
- O workflow final não contém uso de secret, token, login, registry remoto ou publicação.
- Nenhum valor real de credencial foi identificado nos arquivos CI-H3.

## Decisão final

- `SAFE_TO_VERSION_MANUAL_BUILD_ONLY`
- `NO_PUBLISH`
- `NO_SECRETS`
- `NO_REMOTE_PUSH`

## Próxima boundary recomendada

1. `LEGACY-H2 — legacy assets and DOCX large artifact decision`.
2. `TEST-H2 — pytest markers and validation standardization`.
3. `CI-H4 — publish workflow design`, somente se houver decisão humana para publicar imagem.
4. `SEC-H3`, somente se revisão humana confirmar necessidade.
