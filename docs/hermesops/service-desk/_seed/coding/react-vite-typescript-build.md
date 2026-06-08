---
id: "react-vite-typescript-build"
title: "Build React Vite TypeScript com erro"
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
  - "react"
  - "vite"
  - "typescript"
  - "build"
---

## Sintomas comuns
- `vite build` falha com erro de tipo;
- import alias não resolve;
- variável `import.meta.env` ausente;
- bundle quebra após atualização de dependência.

## Comandos de diagnóstico
```bash
npm run build
npx tsc --noEmit
npm ls --depth=0
```

## Boas práticas
- diferenciar erro de TypeScript de erro do bundler;
- validar `tsconfig`, aliases e `vite.config`;
- checar breaking changes de libs atualizadas;
- manter lockfile consistente.

## Riscos
- apagar `node_modules` sem entender lockfile mascara causa;
- corrigir tipo com `any` pode gerar dívida técnica;
- vazar variáveis de ambiente em artefatos de debug.

## Validação
- `tsc --noEmit` passa;
- `npm run build` gera bundle sem erro;
- app roda localmente após build;
- não há warnings críticos novos.

## Rollback
- reverter pacote recém-atualizado;
- restaurar lockfile;
- desfazer alias ou configuração introduzida recentemente.

## Quando chamar Codex
- erro de build com cadeia de dependências complexa;
- necessidade de refatorar tipos ou imports em vários arquivos;
- stack de frontend com regressão difícil de localizar manualmente.

## Quando chamar Gemini
- revisão de UX, arquitetura frontend ou trade-offs de estrutura de projeto;
- comparação entre abordagens de componentização e design system.

## Quando manter local
- segredo em env ou endpoints internos;
- correção pontual em arquivo único;
- build quebrado por configuração local do operador ainda não sanitizada.
