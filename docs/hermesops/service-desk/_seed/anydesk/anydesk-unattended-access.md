---
id: "anydesk-unattended-access"
title: "AnyDesk unattended access com falha de vínculo ou permissão"
document_type: "playbook"
domain: "anydesk"
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
  - "anydesk"
  - "remote"
  - "unattended"
  - "permission"
  - "agent"
---

## Problema
Acesso não assistido via AnyDesk falha mesmo com agente instalado, impedindo suporte remoto a endpoint sem usuário presente.

## Sintomas
- ID responde, mas senha de acesso não funciona;
- dispositivo aparece offline intermitente;
- cliente abre, mas não herda política de unattended access;
- serviço não sobe após reboot.

## Perguntas mínimas
- O agente é corporativo e gerenciado?
- O problema começou após update do cliente?
- O host está com usuário logado ou na tela de lock?
- Existe política central para senha, alias ou ACL?

## Evidências necessárias
- versão do AnyDesk;
- estado do serviço;
- print da tela de erro;
- nome ou ID do dispositivo sem incluir credenciais;
- confirmação de conectividade da máquina.

## Comandos seguros
```powershell
Get-Service AnyDesk -ErrorAction SilentlyContinue
Get-Process AnyDesk -ErrorAction SilentlyContinue
```

## Hipóteses
1. serviço AnyDesk parado;
2. política de unattended access não aplicada;
3. senha ou ACL desatualizada;
4. update quebrou vínculo do cliente;
5. máquina sem reachability adequada.

## Resolução
1. Confirmar se o serviço está instalado e ativo.
2. Validar se o cliente pertence ao tenant ou política correta.
3. Reaplicar configuração gerenciada apenas por procedimento aprovado.
4. Se necessário, reinstalar cliente gerenciado em janela autorizada.
5. Revalidar acesso com teste controlado e owner do endpoint ciente.

## Validação
- serviço sobe automaticamente;
- equipamento aparece online;
- sessão unattended abre com permissões corretas;
- persistência após logoff ou reboot, se aplicável.

## Rollback
- retornar à versão corporativa anterior;
- restaurar perfil de configuração gerenciado que estava funcional.

## Quando escalar
- política central do AnyDesk falha em múltiplos hosts;
- endpoint crítico sem janela de reinstalação;
- suspeita de bloqueio por segurança ou EDR;
- solução remota concorrente aprovada deve ser usada.

## Macro ITIL sugerida
"Analisado acesso não assistido do AnyDesk com foco em serviço, política gerenciada e validação de vínculo do agente, sem exposição de credenciais de acesso remoto."

## Riscos
- manuseio inadequado de senha de unattended access é proibido;
- reinstalação pode remover alias ou vínculo;
- solução remota pode conflitar com política de segurança.
