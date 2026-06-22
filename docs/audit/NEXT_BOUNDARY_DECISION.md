# Next Boundary Decision

Boundary atual: `CLOSE-RUNTIME-DOCKER-H1 - close Dockerfile runtime adjustment`.

## Estado consolidado

```text
GO_RUNTIME_DOCKER_CLOSED
GO_BACKEND_TESTS_OK
PARTIAL_DOCKER_BUILD_NOT_RUN
```

## Decisao objetiva

A boundary runtime/Docker foi fechada em commit separado. O worktree ainda possui grandes árvores untracked e pendências legadas que não devem ser misturadas com a importação Base44.

## Proxima boundary principal

1. `CLOSE-DOCS-LEGACY-H1 - classify docs legacy migration artifacts`
   Objetivo: classificar e separar os artefatos legados, propostas de migração e docs auxiliares fora do frontend e fora do runtime.

## Boundary seguinte

2. `BASE44-FRONTONLY-H1 - import Base44 visual frontend only`
   Condicao: worktree sem pendencias misturadas fora do escopo da importação visual.

## O que nao fazer agora

- Nao executar Docker app build nesta boundary.
- Nao executar `apt-get`.
- Nao tocar em Base44.
- Nao tocar no frontend.
- Nao tocar em package files, migrations, Compose, assets ou data.
- Nao imprimir credenciais, tokens, cookies ou storage state.

## Decisao final

Proxima boundary recomendada: `CLOSE-DOCS-LEGACY-H1 - classify docs legacy migration artifacts`.
