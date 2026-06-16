# CI-H2 — Docker Build/Push Workflow Review

Boundary: `CI-H2 — GitHub Actions docker build/push review without publishing`

## Resumo executivo

Status: `GO` para documentação de auditoria; `NO-GO` para versionar o workflow como está.

Decisão: `NEEDS_CI_H3_HARDENING` e `MANUAL_ONLY_REQUIRED`.

Workflow versionado nesta boundary? não.

Publish executado? não.

Conclusão curta:

- O workflow existe e está untracked em `.github/workflows/docker-build-push.yml`.
- Ele não contém valor real de segredo no YAML analisado.
- Ele usa `secrets.GITHUB_TOKEN` com `packages: write`, o que é tecnicamente coerente para GHCR.
- Porém, ele combina trigger automático `push` em `main`/`master` com `docker/build-push-action` usando `push: true`.
- Se versionado como está, pode publicar imagem automaticamente após push para `main`/`master`.
- Deve ficar fora do Git por enquanto e ser reescrito em `CI-H3` como manual-only/build-only antes de qualquer versionamento.

## Estado Git

Estado inicial observado:

- Branch: `main...origin/main [ahead 17]`.
- Stage inicial: vazio.
- Workflow candidato: `?? .github/workflows/docker-build-push.yml`.
- Commit base recente: `cb27587 chore(git): ignore local sensitive artifacts`.

Garantias desta boundary:

- Workflow não foi alterado.
- Workflow não foi stageado.
- Nenhum push, merge, rebase, tag, GitHub API, GitHub Action, docker login, docker push ou publicação foi executado.

## Arquivo analisado

Path: `.github/workflows/docker-build-push.yml`

Metadado:

- Arquivo existe.
- Tamanho observado: 940 bytes.
- Estado: untracked.

## Triggers

Encontrado:

```yaml
on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:
```

Classificação:

- `push`: presente, para `main` e `master`.
- `workflow_dispatch`: presente.
- `pull_request`: ausente.
- `pull_request_target`: ausente.
- `schedule`: ausente.
- `workflow_run`: ausente.

Risco:

- `push` para `main`/`master` com publish habilitado é risco operacional alto.
- `workflow_dispatch` é positivo, mas não torna o workflow manual-only enquanto `push` existir.

## Permissions

Encontrado:

```yaml
permissions:
  contents: read
  packages: write
```

Análise:

- `contents: read` é mínimo para checkout.
- `packages: write` permite publicar em GHCR com o token do GitHub.
- A permissão é tecnicamente necessária para push em GHCR, mas só deve ser usada em fluxo manual/aprovado.

Decisão:

- Permissões não são excessivas para o objetivo declarado de publicar, mas são perigosas quando combinadas com trigger automático.

## Secrets referenced

Referências encontradas:

- `secrets.GITHUB_TOKEN`

Contextos GitHub usados:

- `github.actor`
- `github.repository_owner`
- `github.sha`

Não encontrado:

- `secrets.DOCKERHUB_USERNAME`
- `secrets.DOCKERHUB_TOKEN`
- `secrets.GHCR_TOKEN`
- valores reais de token/chave/senha.

Classificação:

- Não há exposição de valor secreto no YAML.
- O risco é operacional: o token nativo pode publicar pacote se o workflow for acionado por push.

## Docker login/build-push

Docker login:

```yaml
uses: docker/login-action@v2
registry: ghcr.io
username: ${{ github.actor }}
password: ${{ secrets.GITHUB_TOKEN }}
```

Docker build-push:

```yaml
uses: docker/build-push-action@v5
context: .
push: true
platforms: linux/amd64
```

Classificação:

- Login em GHCR está configurado.
- Publish está explicitamente habilitado.
- Não existe condicional de execução manual no step.

## Publish conditions

Encontrado:

- `push: true` no `docker/build-push-action`.
- Trigger `push` para `main`/`master`.
- Trigger `workflow_dispatch`.

Não encontrado:

- `if: github.event_name == 'workflow_dispatch'`.
- `environment:` protegido.
- Aprovação manual.
- `concurrency:`.
- `push: false` para build-only.

Classificação:

- Publish automático: sim.
- Pode publicar imagem sem aprovação humana adicional depois de versionado e pushado: sim, desde que permissões do repositório permitam `packages: write`.
- Deve ser reescrito antes de versionar: sim.

## Tags

Tags encontradas:

```yaml
ghcr.io/${{ github.repository_owner }}/portal-assinatura:latest
ghcr.io/${{ github.repository_owner }}/portal-assinatura:${{ github.sha }}
```

Análise:

- Tag por SHA é rastreável.
- Tag `latest` é mutável e pode ser sobrescrita automaticamente.
- Nome `portal-assinatura` deve ser confirmado; pode estar ligado ao legado e não necessariamente ao nome operacional atual do Painel ENS-Quality.

Risco:

- Sobrescrita de `latest` sem aprovação.
- Publicação de imagem com nome incorreto ou escopo errado.

## Supply chain

Actions encontradas:

- `actions/checkout@v4`
- `docker/login-action@v2`
- `docker/build-push-action@v5`

Análise:

- Não há uso de `@main`/`@master`, positivo.
- Não há pin por SHA, então ainda há risco residual de supply chain por major tag.
- `docker/login-action@v2` deve ser revisado/atualizado em CI-H3.
- Shell inline encontrado é apenas `echo` informativo; sem comando perigoso.

## actionlint

Resultado:

- `actionlint` não estava instalado.
- Validação actionlint foi pulada sem instalação, conforme regra da boundary.

Classificação:

- `PARTIAL` apenas para lint sintático formal.
- A análise estática manual foi concluída.

## Dockerfile/Compose static context

Arquivos Docker/Compose encontrados por metadado:

- `./backend/Dockerfile`
- `./docker-compose.yml`
- `./infra/hermesops/docker-compose.hml.yml`

Achado relevante:

- O workflow usa `context: .` e não define `file:`.
- O inventário estático encontrou `backend/Dockerfile`, não confirmou um `Dockerfile` na raiz.
- Sem `file: backend/Dockerfile`, o workflow pode falhar ou usar alvo incorreto caso não exista Dockerfile raiz.

Observação:

- Nenhum docker build foi executado.
- Nenhum docker push foi executado.
- Nenhum docker login foi executado.

## Riscos

1. Publish automático em push para `main`/`master`.
2. `packages: write` disponível para workflow automático.
3. `push: true` sem condição manual.
4. Tag `latest` sobrescrita automaticamente.
5. Ausência de `environment` protegido/aprovação.
6. Ausência de `concurrency`.
7. Possível Dockerfile path incorreto: workflow não define `file: backend/Dockerfile`.
8. Nome da imagem `portal-assinatura` precisa validação humana.
9. Actions não estão pinadas por SHA.

## O que NÃO fazer

- Não versionar `.github/workflows/docker-build-push.yml` como está.
- Não rodar `docker login`.
- Não rodar `docker push`.
- Não configurar secrets.
- Não criar tag.
- Não publicar imagem.
- Não transformar `latest` em tag automática sem decisão humana.
- Não acoplar revisão CI com legado, testes, Docker Compose ou código funcional.

## Recomendação

Não versionar este workflow como está.

Abrir `CI-H3 — harden docker build workflow as manual-only, no publish` para reescrever o workflow com uma das abordagens conservadoras:

1. Manual-only e build-only:
   - `on: workflow_dispatch`
   - `push: false`
   - sem login em registry
   - valida apenas build.

2. Manual-only com publish futuro protegido:
   - `on: workflow_dispatch`
   - `environment:` protegido
   - `if: github.event_name == 'workflow_dispatch'`
   - `packages: write` somente se publish for aprovado
   - tags sem sobrescrita automática de `latest`, salvo decisão explícita.

3. Separar CI de release:
   - workflow de CI: build/test sem publish.
   - workflow de release: publish manual/aprovado.

## Próxima boundary

1. `CI-H3 — harden docker build workflow as manual-only, no publish`
2. `LEGACY-H2 — legacy assets and DOCX large artifact decision`
3. `TEST-H2 — pytest markers and validation standardization`

Decisão formal CI-H2: `NEEDS_CI_H3_HARDENING` e `MANUAL_ONLY_REQUIRED`.
