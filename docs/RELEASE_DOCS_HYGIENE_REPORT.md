# Release Docs Hygiene Report

## Objetivo

Garantir que os artefatos de auditoria possam ser versionados sem expor dados sensíveis no contexto de build.

## Constatação

- `.gitignore` não ignora `docs/`; os relatórios de `docs/audit/` e os relatórios da Rodada 2 ficam rastreáveis como arquivos novos no Git.
- `.dockerignore` ignorava `docs/` inteiro e foi reaberto apenas para `docs/audit/*.md`, `docs/audit/*.csv` e `docs/audit/*.txt`.

## Bloqueios preservados

- `.env`
- `secrets/`
- `uat_evidence/`
- backups
- dumps
- bancos locais (`.db`, `.sqlite`, `.sqlite3`)
- arquivos binários de credenciais
- `node_modules/`
- `dist/`

## Observação

- O ajuste foi feito no contexto de build Docker, não no rastreamento do Git.
- Nenhum segredo foi movido ou impresso.
- Índice operacional da auditoria: [docs/audit/README.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/README.md)
