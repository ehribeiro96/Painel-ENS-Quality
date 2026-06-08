# Especificação de CLI do Composio

O plugin deve aparecer no CLI mesmo sem estar habilitado para ações reais.

## Estado exibido

- `status: configured`
- `mode: dry-run`
- `environment: test`
- `api.enabled: false`
- `external_actions_default: blocked`
- write actions bloqueadas
- destructive actions bloqueadas

## Comandos ativos nesta fase

- `hermesops plugins list`
- `hermesops plugins status composio`
- `hermesops composio status`
- `hermesops composio secret check --dry-run`
- `hermesops composio toolkits list --dry-run`
- `hermesops composio logs summarize --dry-run`
- `hermesops composio logs propose-changes --dry-run`

## Saída esperada para `hermesops composio secret check --dry-run`

```text
Composio Secret Check
Fonte: ~/.config/hermesops/secrets/composio.env
Variável: COMPOSIO_API_KEY
Status: presente
Valor: oculto
Permissões: OK
Rede: não chamada
Ações externas: bloqueadas
```

Observação: o valor da chave nunca deve ser impresso.

## Comando futuro documentado, mas bloqueado nesta fase

- `hermesops composio api health --read-only --confirm-network`

Objetivo futuro: validar a API key de forma read-only e confirmada, sem executar toolkits externos. Esse comando não deve ser executado em TEST nesta fase.
