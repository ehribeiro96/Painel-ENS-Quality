# Configuração local de segredo do Composio

## Resumo

- A chave não foi exposta durante esta configuração.
- A chave não foi commitada.
- Nenhuma autenticação externa foi executada.
- Nenhuma API externa foi chamada.
- O plugin ficou `configured`, porém não foi habilitado.

## Arquivo secreto esperado

- Caminho local: `~/.config/hermesops/secrets/composio.env`
- Variável esperada: `COMPOSIO_API_KEY`
- Exemplo de conteúdo esperado no arquivo local (não versionado): `COMPOSIO_API_KEY=<valor real fora do Git>`

## Permissões recomendadas

- Recomendação: `chmod 600 ~/.config/hermesops/secrets/composio.env`
- O valor da chave nunca deve aparecer em terminal, logs, relatórios ou commits.

## Configuração aplicada no repositório

- `plugins/composio/composio.plugin.yaml` agora referencia apenas o caminho local e a variável esperada.
- `api.enabled` continua `false`.
- `status` do plugin foi ajustado para `configured`.
- `mode` continua `dry-run`.
- `environment` continua `test`.
- `external_actions_default` continua `blocked`.
- Write actions continuam bloqueadas.
- Destructive actions continuam bloqueadas.

## Comandos de validação

- `python3 -m py_compile tools/composio_plugin/composio_secret_check.py`
- `python3 -m py_compile tools/hermesops_cli/hermesops_cli.py`
- `hermesops composio secret check --dry-run`
- `hermesops composio status`
- `hermesops plugins status composio`

## Próximo passo recomendado

- Manter a chave fora do Git.
- Em fase posterior e separada, obter aprovação explícita para o futuro comando `hermesops composio api health --read-only --confirm-network` em HML.
- Não habilitar ações externas em TEST.
