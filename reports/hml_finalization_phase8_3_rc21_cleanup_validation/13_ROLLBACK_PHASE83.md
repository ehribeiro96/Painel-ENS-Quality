# Rollback da Fase 8.3

## Sem comandos destrutivos

Não usar:

- git reset --hard
- git clean
- docker compose down -v
- docker volume rm

## Para desfazer commit de higienização

Usar análise humana e preferir:

git revert <commit_da_higienizacao>

## Preservar

- RC2 antigo
- RC2.1
- exports/
- _validation/
- infra/hermesops/.env.hml
- volumes Docker
- imports
- backups
- relatórios
