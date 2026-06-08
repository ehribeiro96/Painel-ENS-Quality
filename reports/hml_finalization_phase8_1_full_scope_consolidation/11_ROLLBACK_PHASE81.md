# Rollback da Fase 8.1

## Sem comandos destrutivos

Não usar:

- `git reset --hard`
- `git clean`
- `docker compose down -v`
- `docker volume rm`

## Se precisar desfazer apenas o commit de consolidação

Usar análise humana antes de qualquer revert.

Preferir:

```bash
git revert <commit_da_fase_8_1>
```

## Preservar

- `infra/hermesops/.env.hml`
- volumes Docker
- backups
- `imports`
- `exports`
- relatórios

## Release candidate

O pacote RC2 pode ser arquivado, mas não deve ser apagado sem aprovação.

