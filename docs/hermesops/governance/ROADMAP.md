
## Composio Plugin — Conexão governada com apps externos e mudanças após logs

- Composio é um plugin externo, visível no CLI e desativado por padrão.
- O modo padrão é `dry-run` e a autenticação real é HML-only.
- Credenciais ficam fora do Git e toolkits seguem allowlist.
- Ações destrutivas são bloqueadas; ações de escrita exigem aprovação humana.
- Logs são sanitizados e podem gerar propostas de mudança, nunca patch automático.
- O pacote HML deve ser regenerado após esta fase.

## HermesOps CLI real e visibilidade do Composio

- `hermesops` é o CLI operacional do HermesOps e é separado do binário oficial `hermes`.
- `hermesops plugins list` expõe Composio como plugin visível.
- `hermesops composio status` mostra Composio como `disabled` / `dry-run` / `HML obrigatório`.
- O Desktop App é aberto via `hermes desktop --cwd /home/ribeiro/Build_Mod/HermesOps`.
- A interface visual do Desktop App não foi alterada nesta fase.
- Logs locais do CLI foram adicionados e mudanças derivadas de logs viram propostas, não patches automáticos.

