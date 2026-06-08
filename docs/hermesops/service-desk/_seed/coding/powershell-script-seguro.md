---
id: "powershell-script-seguro"
title: "Boas práticas para script PowerShell seguro"
document_type: "script_note"
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
  - "powershell"
  - "script"
  - "security"
  - "windows"
---

## Sintomas comuns
- script altera estado sem confirmação;
- uso de `Invoke-Expression`;
- falta de tratamento de erro;
- script remoto exige reboot ou privilégios sem avisar.

## Comandos de diagnóstico
```powershell
Get-Content .\script.ps1
Test-Path .\script.ps1
Set-StrictMode -Version Latest
```

## Boas práticas
- usar `-WhatIf` e `-Confirm` quando aplicável;
- validar parâmetros e caminhos;
- evitar download e execução dinâmica;
- registrar ações sem expor segredos;
- separar funções de leitura e escrita.

## Riscos
- execução remota com privilégio elevado;
- alteração irreversível em registro ou serviços;
- manipulação de credenciais em texto claro;
- impacto em massa se o script for reutilizado sem gating.

## Validação
- script roda em modo de simulação;
- erros são tratados;
- ações destrutivas exigem confirmação humana;
- saída é auditável.

## Rollback
- prover função explícita de reversão quando houver side effect;
- versionar script e manter baseline anterior;
- documentar arquivos e chaves alterados.

## Quando chamar Codex
- revisão de script com fluxo complexo, funções múltiplas ou tratamento de erros insuficiente;
- necessidade de refatorar para modularidade e segurança.

## Quando chamar Gemini
- revisão de UX de prompts, documentação do operador ou desenho de automação;
- avaliação de clareza operacional do script para equipes distintas.

## Quando manter local
- script acessa ambiente restrito;
- presença de credenciais, hosts internos ou trilhas administrativas;
- ajuste simples de lint ou sintaxe já coberto internamente.
