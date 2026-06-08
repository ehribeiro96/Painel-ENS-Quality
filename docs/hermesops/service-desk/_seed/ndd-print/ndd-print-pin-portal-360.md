---
id: "ndd-print-pin-portal-360"
title: "NDD Print Portal 360 - criação ou ajuste de PIN"
document_type: "playbook"
domain: "ndd-print"
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
  - "ndd"
  - "print"
  - "pin"
  - "portal360"
  - "followme"
---

## Problema
Usuário precisa criar, redefinir ou validar PIN de liberação de impressão no NDD Print Portal 360.

## Sintomas
- usuário não consegue liberar impressão na multifuncional;
- PIN informado é recusado;
- primeiro acesso ao portal exige cadastro;
- fila follow-me acumula jobs não liberados.

## Perguntas mínimas
- É primeiro acesso ou redefinição?
- O usuário consegue acessar o Portal 360?
- O bloqueio ocorre em uma impressora ou em todas?
- O vínculo com AD ou crachá já está ativo?

## Evidências necessárias
- mensagem retornada no portal ou painel;
- confirmação de login no portal;
- horário do último teste;
- status da fila retida;
- identificação funcional do usuário sem expor dados pessoais desnecessários.

## Comandos seguros
Comandos locais não são normalmente necessários. Priorizar validação funcional no portal, documentação do procedimento e confirmação de sincronismo de cadastro.

## Hipóteses
1. usuário sem PIN inicial cadastrado;
2. PIN expirado ou digitado incorretamente;
3. atraso de sincronização entre diretório e NDD;
4. equipamento sem atualização do vínculo;
5. bloqueio por política de senha ou PIN.

## Resolução
1. Validar acesso do usuário ao Portal 360.
2. Orientar criação ou redefinição do PIN conforme fluxo homologado.
3. Confirmar critérios mínimos de PIN definidos pela organização.
4. Solicitar novo teste de liberação na impressora correta.
5. Se houver atraso de sincronização, registrar hora e escalar com evidências.

## Validação
- usuário acessa o portal;
- PIN é salvo sem erro;
- liberação de um job de teste funciona;
- fila retida reduz conforme esperado.

## Rollback
- remover alteração apenas se o fluxo de redefinição tiver criado inconsistência em cadastro;
- retornar temporariamente à liberação por outro fator aprovado, se existir processo corporativo.

## Quando escalar
- Portal 360 indisponível;
- vários usuários sem sincronização;
- equipamento não consulta o backend NDD;
- política de PIN divergente da documentação oficial.

## Macro ITIL sugerida
"Usuário orientado em fluxo homologado de criação ou redefinição de PIN no NDD Print Portal 360, com validação de acesso ao portal e teste de liberação de impressão."

## Riscos
- registrar PIN em chamado é proibido;
- reset em conta errada pode bloquear outro usuário;
- tratar falha de sincronismo como erro de digitação mascara problema sistêmico.
