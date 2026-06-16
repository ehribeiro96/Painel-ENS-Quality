# CI-H2 — Workflow Decision Matrix

Boundary: `CI-H2 — GitHub Actions docker build/push review without publishing`

## Workflow

Path: `.github/workflows/docker-build-push.yml`

Estado no Git durante a boundary:

- Arquivo existente.
- Arquivo untracked.
- Arquivo não stageado.
- Arquivo não alterado nesta boundary.
- Workflow não versionado nesta boundary.

## Status

- SAFE_TO_VERSION: `no`
- NEEDS_HARDENING_BEFORE_COMMIT: `yes`
- DO_NOT_COMMIT: `yes, as-is`
- MANUAL_ONLY_RECOMMENDED: `yes`

Decisão resumida: `NEEDS_CI_H3_HARDENING` e `MANUAL_ONLY_REQUIRED` antes de qualquer versionamento.

## Trigger analysis

Triggers encontrados:

- `push` para branches `main` e `master`.
- `workflow_dispatch` manual.

Triggers não encontrados:

- `pull_request`.
- `pull_request_target`.
- `schedule`.
- `workflow_run`.

Risco:

- `push` em `main`/`master` combinado com `push: true` no `docker/build-push-action` gera risco operacional alto: após versionar e fazer push, o workflow pode publicar imagem automaticamente.
- `workflow_dispatch` existe, mas não é manual-only porque o trigger `push` também está habilitado.

## Permission analysis

Bloco encontrado:

```yaml
permissions:
  contents: read
  packages: write
```

Classificação:

- `contents: read`: mínimo/adequado para checkout.
- `packages: write`: necessário para publicar em GHCR, mas perigoso enquanto houver publish automático por `push`.
- Ausência de restrição adicional por `environment`, aprovação manual ou branch gating no job.

Conclusão: permissões são coerentes com publish para GHCR, mas devem ficar acopladas a execução manual e/ou ambiente protegido antes de versionar.

## Secret usage

Secrets/referências encontrados:

- `secrets.GITHUB_TOKEN`
- `github.actor`
- `github.repository_owner`
- `github.sha`

Não foram encontrados valores reais de secrets no YAML.

Classificação:

- Uso de `secrets.GITHUB_TOKEN` é padrão para GHCR quando `packages: write` está habilitado.
- Não há `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` ou token externo explícito.
- Risco principal não é exposição de segredo no YAML; é publish automático com token nativo do GitHub.

## Publish behavior

Configuração encontrada:

```yaml
push: true
```

Condições ausentes:

- Sem `if: github.event_name == 'workflow_dispatch'`.
- Sem `if: github.ref == 'refs/heads/main'` no step de publish, embora o trigger já restrinja branches.
- Sem `environment` protegido.
- Sem aprovação manual.
- Sem modo build-only para PR ou push.

Classificação:

- Publish automático: `yes`, em `push` para `main` e `master`.
- Publish manual: `yes`, via `workflow_dispatch`, mas não exclusivo.
- Build-only: `no`.
- Inseguro/inconclusivo para versionar agora: `yes`.

## Docker tag strategy

Tags encontradas:

- `ghcr.io/${{ github.repository_owner }}/portal-assinatura:latest`
- `ghcr.io/${{ github.repository_owner }}/portal-assinatura:${{ github.sha }}`

Classificação:

- SHA tag é rastreável e positiva.
- `latest` pode ser sobrescrita em qualquer push para `main`/`master`.
- Nome da imagem `portal-assinatura` deve ser confirmado contra o nome atual do produto antes de versionar.

## Supply chain/action pinning

Actions encontradas:

- `actions/checkout@v4`
- `docker/login-action@v2`
- `docker/build-push-action@v5`

Classificação:

- Não usa `@main` ou `@master`; isso é positivo.
- Usa major tags, não SHA pinning. Aceitável para muitos projetos, mas conservadoramente menos forte que pin por SHA.
- `docker/login-action@v2` está uma major atrás do padrão mais atual esperado em muitos workflows; revisar em CI-H3.
- Não há shell inline perigoso além de `echo` informativo.

## Risks

1. Publish automático em push para `main`/`master`.
2. `packages: write` habilitado junto com publish automático.
3. `latest` sobrescrito automaticamente.
4. Ausência de `environment` protegido ou aprovação manual.
5. Ausência de `concurrency`.
6. Workflow não define `file: backend/Dockerfile`; como o único Dockerfile encontrado está em `backend/Dockerfile`, o build com `context: .` pode falhar se não existir `./Dockerfile` raiz.
7. Nome da imagem `portal-assinatura` pode estar desalinhado com o produto atual e precisa decisão humana.

## Required changes before versioning

Antes de versionar, reescrever em boundary própria `CI-H3`:

- Remover trigger `push` ou torná-lo build-only com `push: false`.
- Preferir `workflow_dispatch` manual-only para qualquer publish.
- Adicionar `if: github.event_name == 'workflow_dispatch'` no step de login/publish, se publish for mantido.
- Considerar `environment` protegido para publish.
- Confirmar registry, nome da imagem e política de tags.
- Evitar sobrescrever `latest` sem decisão explícita.
- Definir `file: backend/Dockerfile` ou ajustar Dockerfile/contexto conforme intenção real.
- Considerar `concurrency` para evitar corridas.
- Considerar atualização/pinning de actions em CI-H3.

## Recommended next boundary

`CI-H3 — harden docker build workflow as manual-only, no publish`.

Objetivo recomendado: reescrever o workflow como validação manual/build-only primeiro, sem publicar imagem. Versionamento só depois de revisão humana do desenho final.
