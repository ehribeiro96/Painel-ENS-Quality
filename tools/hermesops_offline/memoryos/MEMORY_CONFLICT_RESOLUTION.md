# Memory Conflict Resolution

Resolução de conflitos sem sobrescrita automática.

## Escopo
- Criar conflito em vez de sobrescrever.
- Registrar evidência e motivo.
- Marcar como conflict_pending até revisão humana.
- Usar supersedes e superseded_by.

## Validação
- Offline only
- Dados sintéticos
- Revisão humana quando aplicável

## Riscos
- Memória ou classificação incorreta se a fonte for fraca
- Conflitos precisam revisão humana

## Rollback
- Remover candidatos inválidos e registrar motivo
