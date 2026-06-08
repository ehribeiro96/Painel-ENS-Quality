---
id: "bsod-eventos-criticos"
title: "BSOD ou eventos críticos recorrentes no Windows"
document_type: "decision_record"
domain: "windows"
status: "draft"
risk_level: "critical"
owner: "Service Desk N2"
source_type: "internal_seed"
sensitivity: "sanitized"
automation_allowed: false
requires_admin: true
external_model_allowed: true
last_review: "2026-06-07"
version: 1
tags:
  - "windows"
  - "bsod"
  - "bugcheck"
  - "eventlog"
  - "driver"
---

## Problema
Endpoint apresenta tela azul, reinícios inesperados ou eventos críticos que indicam falha de driver, hardware ou corrupção de sistema.

## Sintomas
- reinício sem aviso;
- Event ID 41 Kernel-Power;
- BugCheck registrado;
- usuário relata BSOD com código específico;
- falhas começaram após driver ou update.

## Perguntas mínimas
- O evento ocorre durante boot, uso normal ou carga específica?
- Houve update de driver, BIOS ou Windows?
- Existe padrão com docking, VPN, impressão ou vídeo?
- A máquina possui criticidade operacional alta?

## Evidências necessárias
- código de stop se houver;
- Event Viewer com Kernel-Power e BugCheck;
- data e hora dos incidentes;
- driver ou dispositivo suspeito;
- confirmação de existência de minidump sem copiar conteúdo nesta fase.

## Comandos seguros
```powershell
Get-WinEvent -LogName System -MaxEvents 100 | Where-Object {$_.Id -in 41,6008,1001}
wmic recoveros get DebugInfoType,AutoReboot
```

## Hipóteses
1. driver recém-atualizado;
2. falha de memória ou armazenamento;
3. corrupção do sistema;
4. BIOS ou firmware desatualizado;
5. interação com software de segurança.

## Resolução
1. Tratar como incidente de alto risco.
2. Coletar eventos e padrão temporal antes de qualquer tuning.
3. Correlacionar com updates recentes.
4. Se houver mudança recente clara, planejar rollback controlado.
5. Encaminhar para hardware ou engenharia quando houver recorrência ou criticidade.
6. Não prometer correção definitiva sem análise de dump ou evidência do fabricante.

## Validação
- endpoint opera sem novo BSOD por janela observada;
- eventos críticos cessam ou reduzem com causa identificada;
- usuário consegue executar a carga que reproduzia a falha.

## Rollback
- reverter driver ou update recentemente introduzido;
- devolver equipamento reserva se a máquina principal permanecer instável.

## Quando escalar
- qualquer repetição em ativo crítico;
- suspeita de hardware;
- necessidade de análise de dump por time especializado;
- múltiplos endpoints após mesmo update.

## Macro ITIL sugerida
"Incidente tratado como evento crítico de estabilidade do Windows, com coleta de evidências de BugCheck e Kernel-Power, correlação com mudanças recentes e escalonamento controlado conforme impacto."

## Riscos
- risco de perda de dados por reinícios;
- reboot repetido pode corromper perfil e arquivos;
- assumir causa sem dump ou eventos adequados leva a mudança insegura.
