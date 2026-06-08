# 11 Finalization Rollback

## Procedimento seguro
- Restaurar a partir de `_backup/finalization_audit_20260608-132708`
- Preservar volumes Docker existentes
- Preservar `.env.hml`
- Preservar o release candidate gerado
- Preservar os relatórios em `reports/hml_finalization_audit`

## Proibições
- Não usar `git reset --hard`
- Não usar `git clean`
- Não executar `docker compose down -v`
- Não apagar volumes
- Não apagar backups sem relatório

## Observação
- O rollback aqui é de consolidação e release, não de destruição do ambiente.

