# MemoryOS Architecture

Arquitetura baseada em camadas e workflow governado.

## Escopo
- Working memory para contexto temporário.
- Episodic memory para auditorias e troubleshooting.
- Semantic memory para conhecimento consolidado.
- Procedural memory para regras e workflows.

## Validação
- Offline only
- Dados sintéticos
- Revisão humana quando aplicável

## Riscos
- Memória ou classificação incorreta se a fonte for fraca
- Conflitos precisam revisão humana

## Rollback
- Remover candidatos inválidos e registrar motivo
