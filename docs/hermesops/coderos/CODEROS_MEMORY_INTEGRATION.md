# CoderOS Memory Integration

Resumos sanitizados podem virar candidatos de memória; logs brutos não entram em memória.

## Composio

- Composio pode ser tratado como ferramenta candidata com status `disabled` ou `candidate`.
- Ambiente aprovado: HML somente.
- Usar allowlist por toolkit para GitHub, GitLab, Jira e Linear.
- Ações de escrita exigem aprovação; ações destrutivas permanecem bloqueadas.
- Credenciais devem ficar fora do Git.
- Logs geram change proposals, nunca patches automáticos.
