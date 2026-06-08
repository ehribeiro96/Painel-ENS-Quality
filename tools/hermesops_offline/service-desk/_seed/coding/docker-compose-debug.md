---
id: "docker-compose-debug"
title: "Debug de docker compose em ambiente de desenvolvimento"
document_type: "code_debug_note"
domain: "coding"
status: "draft"
risk_level: "medium"
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
  - "docker"
  - "compose"
  - "containers"
  - "healthcheck"
---

## Sintomas comuns
- serviço não sobe;
- healthcheck falha;
- container reinicia em loop;
- volume ou porta em conflito;
- dependência sobe fora de ordem.

## Comandos de diagnóstico
```bash
docker compose config
docker compose ps
docker compose logs --tail=100
```

## Boas práticas
- validar o compose renderizado;
- checar portas, envs e volumes;
- diferenciar falha da aplicação de falha do container;
- manter segredos fora do arquivo compartilhado.

## Riscos
- expor credenciais em `compose.yaml`;
- destruir volume persistente sem backup;
- assumir que `depends_on` garante readiness real.

## Validação
- serviços ficam saudáveis ou estáveis;
- aplicação atende no endpoint esperado;
- logs não mostram crash loop;
- dependências conectam corretamente.

## Rollback
- retornar ao compose anterior;
- restaurar env file anterior;
- subir versão estável da stack.

## Quando chamar Codex
- stack multi-serviço com falha não óbvia;
- necessidade de corrigir compose, Dockerfile e aplicação em conjunto;
- análise de crash loop ligada ao código da app.

## Quando chamar Gemini
- revisão arquitetural de composição de serviços, observabilidade ou desenho de ambiente dev;
- comparação entre alternativas de estrutura.

## Quando manter local
- sem autorização para executar Docker nesta fase;
- segredos ou registries internos presentes;
- ajuste documental sem necessidade de execução externa.
