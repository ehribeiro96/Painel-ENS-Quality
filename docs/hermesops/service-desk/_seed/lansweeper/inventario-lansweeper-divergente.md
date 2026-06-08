---
id: "inventario-lansweeper-divergente"
title: "Inventário Lansweeper divergente do endpoint real"
document_type: "troubleshooting_note"
domain: "lansweeper"
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
  - "lansweeper"
  - "inventory"
  - "scan"
  - "asset"
  - "agentless"
---

## Problema
Inventário exibido no Lansweeper diverge do estado real da máquina, causando erro de decisão sobre software, hardware ou compliance.

## Sintomas
- hostname, serial, software ou uptime inconsistentes;
- equipamento reaparece como ativo antigo;
- scan não atualiza dados recentes;
- software desinstalado continua listado.

## Perguntas mínimas
- O scan é agentless, via credencial remota, ou outro método?
- Quando foi o último scan bem-sucedido?
- Houve rename ou reimage da máquina?
- O ativo está acessível na rede?

## Evidências necessárias
- asset ID do Lansweeper;
- horário do último scan;
- dado divergente específico;
- hostname atual do endpoint;
- confirmação de reachability.

## Comandos seguros
```powershell
hostname
Get-CimInstance Win32_ComputerSystem | Select-Object Name,Model
Get-CimInstance Win32_OperatingSystem | Select-Object LastBootUpTime
```

## Hipóteses
1. scan remoto não executa;
2. ativo duplicado após reimage ou rename;
3. credencial de inventário perdeu acesso;
4. endpoint inacessível;
5. normalização de software atrasada.

## Resolução
1. Comparar dado real do endpoint com o inventário.
2. Verificar data do último scan.
3. Identificar duplicidade ou rename.
4. Acionar owner da ferramenta se houver falha de credencial ou scanner.
5. Não usar inventário divergente como fonte única para ação destrutiva.

## Validação
- próximo scan atualiza o dado esperado;
- duplicidades são tratadas;
- asset correto permanece como referência;
- informação volta a ser confiável para operação.

## Rollback
- reverter fusão ou limpeza incorreta de ativos duplicados;
- restaurar asset marcado indevidamente como obsoleto conforme processo da ferramenta.

## Quando escalar
- falha sistêmica de scanner;
- credenciais do inventário;
- parque inteiro após reimage;
- divergência impactando auditoria ou compliance.

## Macro ITIL sugerida
"Divergência de inventário tratada por comparação entre endpoint real e registro do Lansweeper, com foco em data do scan, duplicidade de ativos e confiabilidade da fonte."

## Riscos
- inventário desatualizado induz decisão errada;
- excluir asset duplicado sem validação pode perder histórico;
- usar dado de scanner como verdade absoluta é inadequado.
