# CoderOS Security Boundaries

Mantém ações destrutivas bloqueadas e exige revisão para qualquer escrita externa.

## Composio

- Composio pode ser tratado como ferramenta candidata com status `disabled` ou `candidate`.
- Ambiente aprovado: HML somente.
- Usar allowlist por toolkit para GitHub, GitLab, Jira e Linear.
- Ações de escrita exigem aprovação; ações destrutivas permanecem bloqueadas.
- Credenciais devem ficar fora do Git.
- Logs geram change proposals, nunca patches automáticos.
