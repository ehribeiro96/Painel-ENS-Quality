---
id: "alembic-migration-debug"
title: "Debug de migração Alembic"
document_type: "code_debug_note"
domain: "coding"
status: "draft"
risk_level: "high"
owner: "Service Desk N2"
source_type: "internal_seed"
sensitivity: "sanitized"
automation_allowed: false
requires_admin: false
external_model_allowed: true
last_review: "2026-06-07"
version: 1
tags:
  - "coding"
  - "alembic"
  - "sqlalchemy"
  - "migration"
  - "database"
---

## Sintomas comuns
- `alembic upgrade head` falha;
- revision chain quebrada;
- coluna já existe ou não existe;
- migration funciona localmente e falha em outro banco.

## Comandos de diagnóstico
```bash
alembic current
alembic history
alembic upgrade head
```

## Boas práticas
- revisar estado real do schema antes de editar migration;
- nunca assumir que todos os ambientes estão no mesmo revision;
- incluir downgrade consistente quando possível;
- testar em banco descartável antes de tocar ambiente compartilhado.

## Riscos
- perda de dados por alteração destrutiva;
- fake migration mascara inconsistência real;
- aplicar correção manual no banco sem registrar cadeia de revisões.

## Validação
- revision atual coincide com o esperado;
- upgrade roda sem erro;
- aplicação inicializa após migration;
- downgrade ou rollback conhecido para mudanças críticas.

## Rollback
- executar downgrade documentado quando seguro;
- restaurar migration anterior no branch;
- usar backup ou snapshot do banco em ambiente apropriado.

## Quando chamar Codex
- cadeia de migrations quebrada com dependências cruzadas;
- necessidade de reescrever migration com segurança;
- análise de compatibilidade entre models e schema real.

## Quando chamar Gemini
- revisão arquitetural sobre estratégia de migração, rollout e governança;
- comparação entre abordagens de evolução de schema.

## Quando manter local
- contexto com dados reais de produção;
- strings de conexão ou esquemas sensíveis não sanitizados;
- ajuste simples em ambiente de teste já compreendido.
