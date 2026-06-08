---
id: "perfil-usuario-corrompido"
title: "Perfil de usuário Windows corrompido"
document_type: "playbook"
domain: "windows"
status: "draft"
risk_level: "high"
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
  - "profile"
  - "temp-profile"
  - "registry"
  - "ntuser"
---

## Problema
Usuário entra com perfil temporário, perde preferências ou não consegue carregar o perfil padrão devido a corrupção local.

## Sintomas
- mensagem de perfil temporário;
- desktop padrão vazio;
- pastas do usuário não refletem histórico;
- eventos User Profile Service;
- login demora excessivamente e termina em perfil temporário.

## Perguntas mínimas
- O problema começou após travamento ou desligamento abrupto?
- O usuário possui dados locais fora de redirecionamento?
- O problema ocorre em outra máquina?
- Houve troca de nome, SID ou restauração recente?

## Evidências necessárias
- Event IDs do User Profile Service;
- caminho do perfil no registro;
- existência de pasta `.bak` associada ao SID;
- confirmação de backup ou redirecionamento dos dados de usuário.

## Comandos seguros
```powershell
Get-WinEvent -LogName Application -MaxEvents 100 | Where-Object {$_.ProviderName -match 'User Profile Service'}
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList'
```

## Hipóteses
1. hive NTUSER.DAT corrompido;
2. SID duplicado com chave `.bak`;
3. antivírus ou backup bloqueando carregamento;
4. falta de espaço em disco;
5. permissões do perfil alteradas.

## Resolução
1. Confirmar se o usuário entrou em perfil temporário.
2. Preservar dados locais antes de qualquer correção estrutural.
3. Revisar chaves `ProfileList` e eventos associados.
4. Se necessário, criar novo perfil controlado e migrar dados de usuário não sensíveis.
5. Só corrigir registro ou permissões em procedimento administrativo autorizado.

## Validação
- login carrega perfil correto;
- favoritos, desktop e AppData essencial reaparecem;
- eventos de User Profile Service cessam;
- usuário confirma retorno das operações essenciais.

## Rollback
- manter perfil antigo preservado para coleta adicional;
- reverter para acesso em outra estação se a recuperação local falhar.

## Quando escalar
- dados locais críticos sem backup;
- corrupção recorrente em várias máquinas da mesma imagem;
- suspeita de problema em GPO, antivírus ou perfil móvel.

## Macro ITIL sugerida
"Identificada falha de carregamento de perfil Windows, com preservação de dados locais e correção orientada por eventos e registro antes de qualquer intervenção destrutiva."

## Riscos
- alteração indevida em `ProfileList` pode piorar o quadro;
- migração apressada pode perder dados locais;
- não preservar evidência impede análise de causa raiz.
