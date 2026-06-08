# 03 Security and Forbidden Files Audit

## Achados no workspace
- Existem arquivos e diretórios permitidos só no workspace, mas proibidos no release final:
  - `.env`
  - `.env.bak_20260603_132713`
  - `.venv/`
  - `frontend/itam-platform/node_modules/`
  - `frontend/itam-platform/dist/`
  - `_backup/`
  - `imports/`
  - `exports/`
  - `__pycache__/`
  - `.ruff_cache/`
- Esses itens não entram no pacote final gerado por `git archive`, mas devem permanecer fora de qualquer staging manual.

## Scan de conteúdo
- Não foi observado segredo real impresso.
- Os hits encontrados são placeholders, referências de documentação e testes:
  - `.env.example`
  - `config/.env.example`
  - `infra/hermesops/.env.hml.example`
  - `README.md`
  - testes e workflows que validam apenas a ausência de segredos
- Também apareceram referências históricas em docs e propostas de migração, mas sem expor valores reais.

## Classificação
- `.env.hml` real continua permitido apenas no workspace e proibido no release.
- `.env.hml.example` é tratado como placeholder, não como segredo.
- Não houve execução do Composio.
- Não houve copy/paste de valores de secret.

## Conclusão
- O risco de segredo real no release candidate gerado a partir do Git rastreado é baixo.
- O risco principal do workspace está nos artefatos gerados localmente e na grande quantidade de untrackeds fora do baseline.

