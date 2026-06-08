# Guia de ativação manual segura do Hermes Desktop CLI

## Objetivo
Ativar manualmente o Hermes Desktop CLI de forma segura usando o wrapper WSL, sem alterar o binário instalado e sem mexer em Registry.

## Caminhos
- Projeto: `/home/ribeiro/Build_Mod/HermesOps`
- Wrapper Bash: `desktop_cli/wrappers/hermes_wsl_launcher.sh`
- Wrapper PowerShell: `desktop_cli/wrappers/hermes_wsl_launcher.ps1`

## Modo recomendado
- Usar o wrapper PowerShell chamando o Bash via WSL.
- Validar com `-DryRun` antes da ativação real.
- Manter `WSL Ubuntu` como backend efetivo.

## Composio no Desktop CLI

- Composio aparece no CLI como plugin disponível, mas desativado por padrão.
- A ativação real só pode ocorrer em HML, com credenciais fora do Git e aprovação humana.
- Logs podem gerar propostas de melhoria, mas não aplicam mudanças automaticamente.
