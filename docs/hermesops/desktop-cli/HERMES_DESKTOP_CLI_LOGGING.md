# Hermes Desktop CLI Logging

- Runtime logs live in `reports/desktop_cli/runtime_logs/`.
- Log filenames should include timestamp and action.
- Logs should capture cwd, project, dry-run state, and the exact Hermes command that would run.
- Logs must never include secret contents.

## Composio no Desktop CLI

- Composio aparece no CLI como plugin disponível, mas desativado por padrão.
- A ativação real só pode ocorrer em HML, com credenciais fora do Git e aprovação humana.
- Logs podem gerar propostas de melhoria, mas não aplicam mudanças automaticamente.
