# CI-H3 — Docker Workflow Hardening

Boundary: `CI-H3 — harden docker build workflow as manual-only, no publish`

## Resumo executivo

Status: `GO` para hardening e versionamento do workflow manual build-only.
Workflow versionado: sim, nesta boundary CI-H3.
Publish executado: não.
Secrets usados: não.

O workflow `.github/workflows/docker-build-push.yml` foi reescrito para validação manual de build Docker, sem publicação de imagem, sem login em registry, sem permissão de escrita em packages e sem trigger automático.

## Estado inicial

Estado observado na FASE 0:

- Branch: `main...origin/main [ahead 18]`.
- Stage inicial: vazio (`git diff --cached --name-status` sem saída).
- Workflow candidato: `?? .github/workflows/docker-build-push.yml`.
- Commit base inicial: `2bef168 docs(ci): review docker build push workflow`.

Estado do workflow antes do hardening:

- Arquivo untracked.
- Tamanho observado: 940 bytes.
- Tinha `push` para `main` e `master`.
- Tinha `workflow_dispatch`.
- Tinha `permissions: packages: write`.
- Tinha `docker/login-action@v2`.
- Tinha `docker/build-push-action@v5` com `push: true`.
- Publicava tags em GHCR, incluindo `latest`.
- Referenciava somente nomes/contextos do GitHub Actions, sem valor real de credencial no YAML.

## Problemas herdados do CI-H2

- trigger push
- packages write
- docker login
- push true
- GHCR
- latest
- Dockerfile path ausente

## Alterações aplicadas

- workflow_dispatch only
- contents read
- setup-buildx
- build-push with push false
- backend/Dockerfile explicit
- no GHCR
- no latest
- no secrets

Detalhe técnico do workflow final:

- `on` contém apenas `workflow_dispatch`.
- `permissions` contém apenas `contents: read`.
- `concurrency` foi adicionado para evitar execuções concorrentes do build manual.
- O job usa `actions/checkout@v4`.
- O job usa `docker/setup-buildx-action@v3`.
- O job usa `docker/build-push-action@v5` com `context: .`, `file: backend/Dockerfile` e `push: false`.
- A tag local de build é `painel-ens-quality/backend:${{ github.sha }}`, sem registry remoto e sem `latest`.

## Validação estática

FASE 4 executada com leitura do YAML final e varredura de padrões proibidos/obrigatórios.

Forbidden patterns verificados:

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

Resultado: sem ocorrências no workflow final.

Required patterns encontrados:

- `workflow_dispatch`
- `contents: read`
- `docker/setup-buildx-action`
- `docker/build-push-action`
- `push: false`
- `file: backend/Dockerfile`
- `context: .`

Resultado: todos encontrados no workflow final.

## actionlint

Resultado: `actionlint not installed; skipping`.

Classificação: ressalva operacional aceitável. Nenhuma instalação foi feita, conforme boundary.

## Riscos restantes

1. O workflow ainda depende de GitHub-hosted runner e actions por major version (`@v4`, `@v3`, `@v5`), sem pin por SHA.
2. O build real não foi executado nesta boundary para evitar consumo pesado e porque o objetivo era hardening estático/manual-only.
3. O Dockerfile executa build frontend e instalação de dependências durante build real; falhas de dependência ou rede só aparecerão em execução futura do workflow manual.
4. A tag usada pelo build action é local/ephemeral no contexto do build, mas ainda deve ser revisada se um fluxo de publish for desenhado no futuro.

## O que NÃO foi feito

- Nenhum `docker login` executado.
- Nenhum `docker push` executado.
- Nenhuma imagem publicada.
- Nenhum secret configurado ou usado.
- Nenhum GitHub Actions real executado.
- Nenhuma chamada à GitHub API executada.
- Nenhum push remoto executado.
- Nenhuma tag Git criada.
- Nenhum Dockerfile alterado.
- Nenhum `docker-compose.yml` alterado.
- Nenhum package-lock alterado.
- Nenhuma migration alterada.
- Nenhum código funcional alterado.
- Nenhum arquivo fora da allowlist CI-H3 alterado.

## Próxima boundary recomendada

1. `LEGACY-H2 — legacy assets and DOCX large artifact decision`.
2. `TEST-H2 — pytest markers and validation standardization`.
3. `CI-H4 — publish workflow design`, somente se houver decisão humana para publicar imagem.
4. `SEC-H3`, somente se revisão humana confirmar necessidade.
