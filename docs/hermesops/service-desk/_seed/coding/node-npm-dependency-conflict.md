---
id: "node-npm-dependency-conflict"
title: "Conflito de dependências Node/NPM"
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
  - "node"
  - "npm"
  - "dependency"
  - "peer-deps"
---

## Sintomas comuns
- `npm install` falha por peer dependency;
- pacote exige versão incompatível de React, ESLint ou Webpack;
- árvore duplica dependências críticas;
- aplicação compila com warning e quebra em runtime.

## Comandos de diagnóstico
```bash
npm install
npm ls
npm explain pacote-problema
```

## Boas práticas
- identificar pacote raiz do conflito;
- preferir alinhamento de versões a `--legacy-peer-deps`;
- revisar changelog do pacote introduzido;
- manter package-lock versionado.

## Riscos
- forçar instalação sem compatibilidade real;
- resolver conflito só no local do operador;
- atualizar cadeia grande de pacotes sem teste mínimo.

## Validação
- instalação conclui sem conflito crítico;
- build e testes passam;
- pacote raiz usa versões coerentes;
- lockfile reproduz o resultado.

## Rollback
- reverter `package.json` e lockfile;
- voltar para versão conhecida do pacote ofensivo;
- remover resolução temporária incompatível.

## Quando chamar Codex
- conflito em cadeia com múltiplos pacotes e peer dependencies;
- necessidade de propor combinação estável de versões;
- análise de impacto em monorepo ou workspace.

## Quando chamar Gemini
- revisão arquitetural sobre troca de biblioteca, bundler ou framework;
- avaliação comparativa entre caminhos de modernização.

## Quando manter local
- conflito simples e já reproduzido;
- contexto inclui registries privados ou pacotes internos não sanitizados;
- lockfile corporativo ainda não pode ser compartilhado externamente.
