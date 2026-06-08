# HermesOps HML Environment Policy

## Regra central

`.env.hml` real nao deve ser versionado.

## Permitido versionar

- `.env.hml.example`
- documentacao de variaveis
- placeholders

## Proibido versionar

- `.env`
- `.env.hml`
- tokens
- API keys
- passwords reais
- certificados
- chaves privadas

## Composio

`COMPOSIO_API_KEY` deve permanecer fora do Git.

Qualquer uso futuro deve ser:

- read-only primeiro;
- sem tools/execute;
- sem connected account automatica;
- com aprovacao humana.

## Docker

Variaveis devem ser validadas com:

`docker compose config`

antes de qualquer runtime.
