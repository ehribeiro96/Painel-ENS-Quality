# HermesOps pt-BR String Audit

## Escopo
Auditoria dos textos visíveis do painel HermesOps/Composio no Desktop patchado.

## Strings que devem virar pt-BR
- `Dashboard` -> `Painel`
- `Read-only` -> `Somente leitura`
- `Mock bridge` -> `Bridge simulado`
- `Source` -> `Fonte`
- `Locale and launcher` -> `Localidade e inicializador`
- `Keyboard metadata` -> `Metadados do teclado`
- `No keyboard events yet` -> `Nenhum evento de teclado ainda`
- `Press any key in the Desktop window to capture safe metadata` -> `Pressione qualquer tecla na janela do Desktop para capturar metadados seguros`
- `Read-only actions` -> `Ações somente leitura`
- `Blocked Actions` -> `Ações bloqueadas`
- `Secret Check` -> `Verificar segredo`
- `Toolkits List --dry-run` -> `Listar toolkits --dry-run`
- `Permissions Audit --dry-run` -> `Auditar permissões --dry-run`
- `Logs Summarize --dry-run` -> `Resumir logs --dry-run`
- `Propose Changes --dry-run` -> `Propor mudanças --dry-run`
- `Enable Plugin` -> `Habilitar plugin`
- `Connect Account` -> `Conectar conta`
- `Execute Tool` -> `Executar ferramenta`
- `Send Email` -> `Enviar e-mail`
- `Create Issue` -> `Criar issue`
- `Delete` -> `Excluir`
- `Write Action` -> `Ação de escrita`
- `Admin Action` -> `Ação administrativa`
- `Browser locale` -> `Localidade do navegador`
- `Accepted languages` -> `Idiomas aceitos`
- `Launcher wrapper` -> `Wrapper de inicialização`
- `Plugin inventory` -> `Inventário de plugins`
- `Bridge posture` -> `Postura do bridge`
- `Credential state` -> `Estado da credencial`
- `Execution policy` -> `Política de execução`
- `No local log entries yet` -> `Nenhuma entrada de log local ainda`
- `Use the safe buttons in the Composio tab to seed local trace entries` -> `Use os botões seguros na aba Composio para criar entradas locais de rastreio`
- `Health check da API` and related labels should stay coherent in pt-BR

## Termos técnicos que permanecem em inglês
- `HermesOps`
- `Composio`
- `dry-run`
- `mock/read-only`
- `API`
- `MCP`
- `HML`
- `pt-BR`
- `f529068+`
- `hermes-agent-hermesops`
- `COMPOSIO_API_KEY`
- `GET /api/v3.1/tools`
- `KeyboardEvent.key`
- `KeyboardEvent.code`
- `AltGr`
- `navigator.language`
- `navigator.languages`

## Comandos que permanecem literais
- `hermesops composio secret check --dry-run`
- `hermesops composio api health --read-only`
- `hermesops composio api health --confirm-network`
- `hermesops composio api health --read-only --confirm-network`
- `hermesops composio api health --read-only --confirm-network --dry-run`
- `--read-only`
- `--confirm-network`
- `--dry-run`
- `x-api-key`

## Observação
O painel HermesOps já foi traduzido de forma consistente em pt-BR sem expor segredos ou ativar chamadas externas no renderer.
