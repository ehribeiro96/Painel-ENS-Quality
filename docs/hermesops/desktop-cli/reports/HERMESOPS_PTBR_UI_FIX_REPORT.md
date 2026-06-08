# HermesOps pt-BR UI Fix Report

## Resumo
O painel HermesOps/Composio do Desktop foi padronizado em pt-BR, mantendo os termos técnicos que precisam continuar literais e preservando o modo seguro/mock/read-only.

## Mudanças no Desktop
- Criei `src/app/settings/hermesops-i18n.ts` com o dicionário pt-BR local.
- Traduzi os rótulos visíveis do painel HermesOps.
- Mantive `HermesOps`, `Composio`, `dry-run`, `mock/read-only`, `API`, `MCP`, `HML`, `pt-BR`, `f529068+`, `hermes-agent-hermesops` e `COMPOSIO_API_KEY` como termos literais.
- Ajustei o bloco de Composio para deixar explícito que nenhuma API real foi chamada.
- Adicionei a seção de `Health check da API` em modo bloqueado na UI.
- Adicionei o botão visual desabilitado `Executar health check read-only`.
- Reforcei o callout da sidebar para apontar o painel HermesOps/Composio.

## Mudanças no CLI
- Adicionei `hermesops composio api health`.
- O comando exige `--read-only` e `--confirm-network`.
- O modo `--dry-run` só mostra o plano.
- O health check faz apenas `GET /api/v3.1/tools`.
- A chave fica oculta e não é registrada em nenhum log.

## Validações
- `python3 -m py_compile tools/hermesops_cli/hermesops_cli.py`
- `hermesops composio status`
- `hermesops composio secret check --dry-run`
- `hermesops composio api health --read-only`
- `hermesops composio api health --confirm-network`
- `hermesops composio api health --read-only --confirm-network --dry-run`
- `npm run type-check`
- `npx eslint src/app/settings/index.tsx src/app/settings/hermesops-settings.tsx`

## Observação de segurança
Nenhuma chamada real ao Composio foi executada nesta etapa. O renderer continua sem acesso à `COMPOSIO_API_KEY`.
