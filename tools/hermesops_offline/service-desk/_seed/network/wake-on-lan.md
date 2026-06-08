---
id: "wake-on-lan"
title: "Wake-on-LAN para ligar estação remotamente"
document_type: "vendor_reference"
domain: "network"
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
  - "network"
  - "wol"
  - "bios"
  - "nic"
  - "magic-packet"
---

## Problema
Necessidade de energizar remotamente uma estação desligada usando Wake-on-LAN, sem presença física do usuário.

## Sintomas
- máquina não responde enquanto desligada;
- pacote enviado não produz boot;
- host desperta apenas de sleep, não de shutdown;
- solução funciona em algumas VLANs e falha em outras.

## Perguntas mínimas
- A placa e BIOS suportam WoL em estado S5?
- O equipamento é ligado por cabo ou Wi-Fi?
- A rede permite broadcast ou relay para WoL?
- O MAC address foi validado em fonte confiável?

## Evidências necessárias
- modelo da máquina;
- estado de energia testado (sleep, hibernate ou shutdown);
- NIC usada;
- VLAN ou site;
- resultado do envio do pacote e horário.

## Comandos seguros
```powershell
Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}
powercfg /devicequery wake_armed
```

## Hipóteses
1. BIOS desabilitada para WoL;
2. NIC sem opção de wake armada;
3. WoL via Wi-Fi não suportado;
4. rede bloqueando broadcast;
5. MAC address incorreto.

## Resolução
1. Validar suporte do hardware e política corporativa.
2. Confirmar uso de NIC cabeada.
3. Checar configurações de energia do adaptador e BIOS ou UEFI.
4. Usar ferramenta homologada para envio do magic packet.
5. Se necessário, alinhar com rede para relay específico.

## Validação
- host liga após pacote;
- comportamento é repetível;
- evento de boot confirma horário do wake;
- usuário consegue prosseguir com suporte remoto.

## Rollback
- desabilitar opção de wake se houver ativação indevida fora do expediente;
- remover configuração experimental de relay ou broadcast na rede.

## Quando escalar
- necessidade de mudança em switch ou router;
- BIOS bloqueada pela imagem;
- parque inteiro sem suporte;
- impacto energético ou compliance.

## Macro ITIL sugerida
"Validado cenário de Wake-on-LAN com foco em hardware, BIOS, NIC e capacidade da rede de transportar o magic packet de forma homologada."

## Riscos
- WoL pode falhar por limitação física e não por software;
- testes em broadcast mal controlado geram ruído na rede;
- uso de MAC desatualizado leva a falso diagnóstico.
