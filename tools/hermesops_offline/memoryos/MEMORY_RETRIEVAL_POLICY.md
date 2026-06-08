# Memory Retrieval Policy

Prioridade de recuperação e filtros obrigatórios.

## Escopo
- priorizar approved
- candidate apenas com aviso
- bloquear secret
- restringir restricted a uso local
- filtrar por environment, domain, risk_level, sensitivity e external_model_allowed

## Validação
- Offline only
- Dados sintéticos
- Revisão humana quando aplicável

## Riscos
- Memória ou classificação incorreta se a fonte for fraca
- Conflitos precisam revisão humana

## Rollback
- Remover candidatos inválidos e registrar motivo
