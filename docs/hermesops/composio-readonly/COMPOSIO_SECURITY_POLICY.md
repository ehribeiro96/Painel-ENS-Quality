# Política de segurança do Composio

## Credencial local fora do Git

- A `COMPOSIO_API_KEY` deve ficar somente em `~/.config/hermesops/secrets/composio.env`.
- A variável esperada é `COMPOSIO_API_KEY`.
- O valor nunca pode ser versionado, salvo em `plugins/composio/composio.plugin.yaml`, memória, relatórios ou logs.
- `env_file_allowed: false` significa que `.env` do repositório é proibido.
- `git_storage_allowed: false`, `memory_storage_allowed: false` e `log_storage_allowed: false` são mandatórios.

## Estado operacional obrigatório

- `test` nunca autentica toolkits externos.
- `dry-run` é o padrão obrigatório nesta fase.
- `configured` significa apenas que a fonte local do segredo foi declarada; não significa `enabled`.
- `api.enabled` permanece `false` até HML com aprovação.
- `external_actions_default` deve permanecer `blocked`.
- Write actions continuam bloqueadas.
- Destructive actions continuam bloqueadas.

## Validação segura

- Validar localmente com `hermesops composio secret check --dry-run`.
- O comando deve informar apenas presença/ausência da chave, nunca o valor.
- O arquivo local deve preferencialmente usar permissão `600`.
- Caso a permissão esteja mais aberta, recomendar `chmod 600 ~/.config/hermesops/secrets/composio.env`.

## Fora de escopo nesta fase

- Não chamar API real do Composio.
- Não autenticar Gmail, GitHub, Drive, M365 ou qualquer toolkit externo.
- Não executar ações externas reais.
- Não habilitar o plugin em produção.
