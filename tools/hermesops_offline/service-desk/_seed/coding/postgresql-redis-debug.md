---
id: "postgresql-redis-debug"
title: "Debug de integração PostgreSQL e Redis"
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
  - "postgresql"
  - "redis"
  - "cache"
  - "connection"
---

## Sintomas comuns
- timeout de conexão;
- credencial errada;
- cache inconsistente;
- aplicação conecta ao banco, mas não ao Redis;
- pool esgota sob carga.

## Comandos de diagnóstico
```bash
psql --version
redis-cli --version
ss -ltnp | grep -E '5432|6379'
```

## Boas práticas
- validar separadamente banco e cache;
- checar DSN e URL sem expor senha;
- confirmar readiness e autenticação;
- medir se o erro é de rede, credencial ou aplicação.

## Riscos
- compartilhar connection string com segredo;
- limpar Redis em ambiente indevido;
- executar SQL corretivo sem entender impacto transacional.

## Validação
- conexão a ambos os serviços funciona;
- app executa fluxo que depende de banco e cache;
- logs de pool ou timeout reduzem;
- endpoint crítico responde.

## Rollback
- voltar DSN ou config anterior;
- reverter alteração de pool ou timeouts;
- desabilitar cache apenas se houver fallback documentado.

## Quando chamar Codex
- falha distribuída envolvendo código, drivers e pool de conexões;
- necessidade de revisar camada de acesso a dados e cache;
- correlação entre timeout e implementação da aplicação.

## Quando chamar Gemini
- revisão arquitetural de desenho de cache, consistência ou topologia de serviços;
- avaliação de trade-offs entre estratégias de resiliência.

## Quando manter local
- credenciais reais ou topologia interna não sanitizada;
- incidente ligado ao ambiente corporativo restrito;
- troubleshooting simples de conectividade local.
