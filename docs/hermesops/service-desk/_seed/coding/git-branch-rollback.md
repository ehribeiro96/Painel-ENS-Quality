---
id: "git-branch-rollback"
title: "Rollback seguro de branch Git"
document_type: "decision_record"
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
  - "git"
  - "rollback"
  - "branch"
  - "revert"
---

## Sintomas comuns
- branch ficou quebrada após merge ou refactor;
- commit recente introduziu regressão;
- conflito resolvido de forma incorreta;
- build verde anterior agora falha.

## Comandos de diagnóstico
```bash
git status
git log --oneline --decorate -n 20
git diff --stat
```

## Boas práticas
- decidir entre `revert`, `restore` ou reset conforme compartilhamento da branch;
- preservar trabalho não commitado antes de rollback;
- validar CI local mínima após reversão;
- documentar o commit causador.

## Riscos
- `reset --hard` em branch compartilhada;
- perda de mudanças locais;
- rollback parcial deixando o estado inconsistente.

## Validação
- branch volta a compilar ou testar;
- commit problemático fica claramente neutralizado;
- histórico continua compreensível para o time.

## Rollback
- se o revert foi incorreto, reverter o revert;
- restaurar stash ou branch temporária criada para preservar trabalho;
- retomar da tag ou commit estável conhecido.

## Quando chamar Codex
- sequência complexa de commits e conflitos;
- necessidade de identificar o ponto exato da regressão;
- rollback com impacto em múltiplos módulos.

## Quando chamar Gemini
- revisão do processo de branch strategy, governança ou fluxo de release;
- discussão arquitetural sobre como evitar regressões semelhantes.

## Quando manter local
- branch com código sensível ou privado não sanitizado;
- rollback direto e já comprovado pelo histórico;
- necessidade de preservar contexto interno do repositório.
