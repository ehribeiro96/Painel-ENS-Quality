---
id: "python-fastapi-debug"
title: "Debug de aplicação Python FastAPI"
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
  - "python"
  - "fastapi"
  - "uvicorn"
  - "api"
---

## Sintomas comuns
- API sobe e cai imediatamente;
- erro 500 em rota específica;
- import circular;
- erro de validação Pydantic;
- endpoint assíncrono trava sob carga local.

## Comandos de diagnóstico
```bash
python3 --version
python3 -m py_compile app/main.py
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pytest -q
```

## Boas práticas
- reproduzir primeiro em ambiente local controlado;
- isolar erro de import antes de testar HTTP;
- validar schema de request e response;
- revisar variáveis obrigatórias sem registrar segredos no log.

## Riscos
- expor `.env` ou credenciais em stack trace compartilhada;
- testar contra banco real sem isolamento;
- confundir bug de aplicação com erro de dependência do ambiente.

## Validação
- app sobe sem exception;
- rota crítica responde código esperado;
- testes mínimos passam;
- logs não mostram regressão imediata.

## Rollback
- reverter commit ou branch da alteração recente;
- restaurar dependências lockadas;
- voltar para configuração funcional anterior de uvicorn ou app factory.

## Quando chamar Codex
- bug complexo em código com necessidade de raciocínio de implementação;
- análise de stack trace extensa;
- refatoração controlada com contexto mínimo e sanitizado.

## Quando chamar Gemini
- revisão de UX, arquitetura, documentação comparativa ou alternativas de design;
- necessidade de segunda opinião em trade-offs sem expor segredos.

## Quando manter local
- contexto com sensibilidade alta ou secreta;
- ajuste simples e reproduzível com logs locais mínimos;
- quando o problema está claramente ligado ao ambiente corporativo não sanitizado.
