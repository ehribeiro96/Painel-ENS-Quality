---
id: "maquina-sem-rede"
title: "Máquina sem conectividade de rede"
document_type: "playbook"
domain: "network"
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
  - "network"
  - "ethernet"
  - "wifi"
  - "dhcp"
  - "gateway"
---

## Problema
Estação está sem acesso à rede local ou internet corporativa, impedindo autenticação, acesso a sistemas e suporte remoto.

## Sintomas
- ícone de rede desconectado ou limitado;
- IP APIPA;
- sem acesso a gateway, DNS ou VPN;
- apenas alguns destinos respondem;
- rede cai após retorno de suspensão.

## Perguntas mínimas
- É conexão cabeada, Wi-Fi ou docking station?
- O problema afeta apenas a máquina ou outros no mesmo ponto?
- A placa de rede aparece habilitada?
- Houve mudança de mesa, switch, docking ou VLAN?

## Evidências necessárias
- resultado de `ipconfig /all`;
- teste de ping para gateway;
- status do adaptador;
- identificação do ponto de rede ou SSID;
- horário de início da falha.

## Comandos seguros
```powershell
Get-NetAdapter
Get-NetIPConfiguration
Test-NetConnection 8.8.8.8 -InformationLevel Quiet
```

```cmd
ipconfig /all
```

## Hipóteses
1. cabo, dock ou NIC com falha;
2. DHCP não entregando lease;
3. perfil Wi-Fi incorreto;
4. VLAN ou porta bloqueada;
5. pilha TCP/IP local inconsistente.

## Resolução
1. Isolar camada física primeiro.
2. Validar estado do adaptador e IP recebido.
3. Testar gateway antes de testar internet.
4. Renovar lease somente após coletar evidências.
5. Se houver docking, testar NIC direta.
6. Se escopo for coletivo, envolver rede imediatamente.

## Validação
- adaptador sobe corretamente;
- IP, gateway e DNS coerentes;
- gateway responde;
- acesso ao recurso corporativo esperado retorna.

## Rollback
- restaurar perfil de rede anterior;
- reverter ajuste manual de IP se ele foi usado apenas para teste controlado.

## Quando escalar
- suspeita de switch ou VLAN;
- site com múltiplas máquinas afetadas;
- bloqueio por NAC ou segurança;
- endpoint crítico sem alternativa de conectividade.

## Macro ITIL sugerida
"Executado diagnóstico em camadas para falha de rede, com coleta de IP e configuração, teste ao gateway e isolamento entre causa física, DHCP, perfil e infraestrutura."

## Riscos
- reinicializar pilha cedo demais apaga evidências;
- IP manual temporário pode mascarar problema de DHCP;
- tratar incidente de rede como falha individual atrasa resposta.
