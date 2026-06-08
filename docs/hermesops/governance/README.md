
## Composio Plugin — credencial local fora do Git e ativação governada

- A `COMPOSIO_API_KEY` deve ficar somente em `~/.config/hermesops/secrets/composio.env`.
- O valor da chave nunca deve ser logado, impresso em terminal, salvo em memória, relatórios com segredo ou commitado no Git.
- `plugins/composio/composio.plugin.yaml` referencia apenas o caminho local e a variável `COMPOSIO_API_KEY`; nenhum valor secreto é armazenado no repositório.
- Plugin `configured` não significa plugin habilitado: o Composio continua em `dry-run`, `test`, com `api.enabled: false`.
- `external_actions_default` permanece `blocked`.
- Write actions continuam bloqueadas.
- Destructive actions continuam bloqueadas.
- Execução real, autenticação de toolkits e chamadas externas só podem acontecer em HML com aprovação explícita.
- Validação local segura: `hermesops composio secret check --dry-run`.
- Comando futuro documentado, mas bloqueado nesta fase: `hermesops composio api health --read-only --confirm-network`.
