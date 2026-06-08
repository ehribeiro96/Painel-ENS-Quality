# Phase 5.1 Compose Promotion Decision Matrix

| Opção | Status | Vantagem | Risco | Decisão |
| --- | --- | --- | --- | --- |
| Manter staging | seguro | baixo risco | pouca clareza operacional | rejeitado |
| Promover canonical-config | melhor equilíbrio | configura referência oficial sem runtime | exige disciplina para não executar up | recomendado |
| Promover runtime | integração real | alto risco | exige env/secrets/rollback | bloqueado |
| Bloquear | máximo conservadorismo | trava evolução | desnecessário após config OK | rejeitado |

## Decisão recomendada
- Promover para `canonical-config`, sem runtime.
