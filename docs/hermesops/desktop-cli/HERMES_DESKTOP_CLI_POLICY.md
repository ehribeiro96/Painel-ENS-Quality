# Hermes Desktop CLI Policy

- Hermes Desktop is the interface; WSL Ubuntu is the backend source of truth.
- Project commands must default to `/home/ribeiro/Build_Mod/HermesOps`.
- `System32` and other Windows roots are forbidden as launch directories.
- CLI changes must be auditable and reversible.
- The installed Hermes binary must not be edited directly.
- Future app-level modifications require a separate branch and explicit backup.

## Composio no Desktop CLI

- Composio aparece no CLI como plugin disponível, mas desativado por padrão.
- A ativação real só pode ocorrer em HML, com credenciais fora do Git e aprovação humana.
- Logs podem gerar propostas de melhoria, mas não aplicam mudanças automaticamente.
