# Hermes Desktop CLI Customization

This layer documents and wraps the Hermes Desktop CLI so the Windows desktop app remains the interface while WSL Ubuntu stays the source of truth for project execution.

Key ideas:
- Desktop: UI only
- WSL Ubuntu: real backend
- Project root: `/home/ribeiro/Build_Mod/HermesOps`
- Safe logs: `reports/desktop_cli/`
- Rollback: documented and tested

See the companion architecture, policy, discovery, wrapper plan, rollback, logging, and routing docs in this directory.
