# Composio API Health Check Endpoint Fix

## Resumo

O health check do Composio no `hermesops` retornava HTTP 404 com HTML porque usava a base antiga/incorreta `https://connect.composio.dev` combinada com `/api/v3.1/tools`.

## Causa raiz

A API key estava válida. O teste direto com `curl` na URL correta retornou HTTP 200 e JSON válido. A falha estava na base URL/rota do CLI.

## Correção

Base REST corrigida para:

`https://backend.composio.dev/api/v3.1`

Endpoint read-only corrigido para:

`/tools?toolkit_versions=latest`

URL final:

`https://backend.composio.dev/api/v3.1/tools?toolkit_versions=latest`

## Segurança

- API key não foi impressa.
- API key não foi versionada.
- API key não foi enviada ao renderer.
- Nenhuma tool foi executada.
- Nenhuma connected account foi criada.
- Nenhuma ação externa foi realizada.
- Health check exige `--read-only` e `--confirm-network`.

## Resultado

- dry-run: OK
- validação flags obrigatórias: OK
- health check real: HTTP 200
- content-type: application/json
- tools retornadas: 20
- status final: OK
