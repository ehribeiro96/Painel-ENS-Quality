---
id: "impressora-nao-imprime"
title: "Impressora instalada não imprime"
document_type: "kcs_article"
domain: "printers"
status: "draft"
risk_level: "medium"
owner: "Service Desk N2"
source_type: "internal_seed"
sensitivity: "sanitized"
automation_allowed: false
requires_admin: true
external_model_allowed: true
last_review: "2026-06-07"
version: 1
tags:
  - "printer"
  - "spooler"
  - "fila"
  - "driver"
  - "tcpip"
---

## Problema
Impressora está instalada, aparece online ou compartilhada, mas jobs não saem ou ficam presos na fila.

## Sintomas
- documento permanece em spool;
- job some sem imprimir;
- teste local falha;
- fila trava após um job específico;
- impressora responde ping, mas não imprime.

## Perguntas mínimas
- É impressora local TCP/IP, compartilhada ou por servidor de impressão?
- O problema afeta um usuário, uma fila ou vários?
- Outros usuários imprimem normalmente?
- Houve troca recente de driver ou IP da impressora?

## Evidências necessárias
- nome exato da fila;
- tipo de conexão;
- print da fila;
- horário do último job;
- mensagem do spooler ou código do driver.

## Comandos seguros
```powershell
Get-Printer
Get-PrintJob -PrinterName "NOME_DA_FILA"
Get-Service Spooler
```

```cmd
rundll32 printui.dll,PrintUIEntry /s /t2
```

## Hipóteses
1. spooler travado;
2. fila presa por job corrompido;
3. driver errado ou porta incorreta;
4. impressora sem papel, toner ou com erro físico;
5. fila apontando para IP antigo.

## Resolução
1. Identificar escopo: local, fila compartilhada ou dispositivo.
2. Limpar fila somente após confirmar jobs descartáveis.
3. Reiniciar spooler de forma controlada se houver travamento.
4. Validar porta, IP ou servidor de impressão.
5. Se o problema for driver, alinhar com modelo homologado.
6. Em impressora de rede, validar status físico antes de mexer no Windows.

## Validação
- página de teste imprime;
- fila esvazia sem erro;
- novo job do usuário conclui;
- não há travamento recorrente do spooler.

## Rollback
- restaurar driver ou porta previamente utilizados;
- readicionar fila antiga caso a recriação da fila não funcione.

## Quando escalar
- falha física do equipamento;
- fila crítica em servidor de impressão;
- driver proprietário não homologado;
- múltiplas filas com travamento simultâneo.

## Macro ITIL sugerida
"Realizada análise da fila de impressão, spooler e conectividade da impressora, com saneamento controlado da fila e validação por página de teste."

## Riscos
- limpar fila sem autorização pode perder impressão importante;
- reinício do spooler impacta outras impressoras do host ou servidor;
- troca de driver incorreta afeta digitalização e finishing.
