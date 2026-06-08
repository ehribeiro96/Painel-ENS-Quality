# HermesOps HML Compose Usage Policy

## Status

`canonical-config`

Este Compose e o candidato canônico de configuração HML para HermesOps.

Ele esta autorizado para:

- leitura;
- auditoria;
- `docker compose config`;
- revisao de configuracao;
- planejamento de runtime.

Ele NAO esta autorizado para:

- `docker compose up`;
- `docker compose down`;
- `docker compose down -v`;
- criacao de volumes;
- execucao de Composio;
- execucao de connected accounts;
- deploy.

## Arquivo

`infra/hermesops/docker-compose.hml.yml`

## Env real

`.env.hml` real deve ser criado manualmente em fase posterior, fora do Git.

## Env example

`.env.hml.example` contem apenas placeholders e defaults nao sensiveis.

## Critérios para runtime futuro

Antes de qualquer `up`:

1. criar `.env.hml` real fora do Git;
2. validar secrets;
3. validar `docker compose config`;
4. criar backup;
5. validar volumes;
6. validar ports;
7. revisar servicos;
8. revisar rollback;
9. aprovacao humana explicita.
