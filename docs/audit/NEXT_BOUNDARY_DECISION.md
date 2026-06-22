# Next Boundary Decision

Boundary atual: `CLOSE-DOCS-LEGACY-H1 - classify docs legacy migration artifacts before Base44 import`.

## Estado consolidado

```text
GO_DOCS_LEGACY_CLASSIFIED
PARTIAL_GITIGNORE_UPDATED
PARTIAL_LEGACY_ASSETS_LEFT_UNTRACKED
```

## Decisao objetiva

Os artefatos legados e de documentação local foram classificados. A importação Base44 ainda deve aguardar até o worktree ficar limpo de alterações rastreadas fora do escopo.

## Proxima boundary principal

1. `BASE44-FRONTONLY-H1 - import Base44 visual frontend only`

## Boundaries opcionais, se houver tempo ou necessidade de governance

2. `LEGACY-ASSETS-H1 - decide archive policy for legacy assets`
3. `MIGRATION-PROPOSALS-H1 - review HermesOps selective migration proposals`

## O que nao fazer agora

- Nao importar Base44 ainda.
- Nao tocar no frontend atual.
- Nao tocar no backend, Dockerfile, migrations ou package files.
- Nao commitar assets legados, screenshots ou runtime databases.
- Nao imprimir credenciais, tokens, cookies ou storage state.

## Decisao final

Proxima boundary recomendada: `BASE44-FRONTONLY-H1 - import Base44 visual frontend only`.
