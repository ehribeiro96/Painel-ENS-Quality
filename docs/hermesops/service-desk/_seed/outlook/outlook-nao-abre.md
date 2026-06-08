---
id: "outlook-nao-abre"
title: "Outlook não abre após atualização ou falha de perfil"
document_type: "troubleshooting_note"
domain: "outlook"
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
  - "outlook"
  - "office"
  - "perfil"
  - "addin"
  - "ost"
  - "clicktorun"
---

## Problema
Outlook não inicia, fecha imediatamente ou fica preso em splash screen após atualização do Office, corrupção de perfil ou falha em add-in COM.

## Sintomas
- janela do Outlook abre e fecha sem erro claro;
- splash screen permanece em processamento;
- execução em modo seguro funciona;
- Event Viewer registra falha em OUTLOOK.EXE ou DLL de add-in;
- usuário informa que o problema começou após update do Microsoft 365 Apps.

## Perguntas mínimas
- O problema ocorre com todos os usuários da máquina ou apenas com um perfil?
- O Outlook abre com `outlook.exe /safe`?
- Houve atualização recente do Office, Windows ou add-in fiscal/assinatura?
- O usuário trabalha com mailbox compartilhada grande ou OST local muito antigo?

## Evidências necessárias
- captura do erro ou comportamento;
- versão do Office/Click-to-Run;
- lista de add-ins habilitados;
- tamanho aproximado do OST;
- Event ID ou Application Error correspondente.

## Comandos seguros
```powershell
outlook.exe /safe
Get-Process OUTLOOK -ErrorAction SilentlyContinue
Get-Item "C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE"
```

```cmd
control mlcfg32.cpl
```

## Hipóteses
1. add-in de terceiros quebrando inicialização;
2. perfil MAPI corrompido;
3. OST local inconsistente;
4. build do Office com regressão;
5. credencial moderna travada em cache local.

## Resolução
1. Testar modo seguro.
2. Se abrir, desabilitar add-ins não Microsoft e reabrir normalmente.
3. Criar novo perfil de correio sem excluir o perfil antigo.
4. Se persistir, fechar Outlook e renomear OST para rebuild controlado.
5. Validar reparo rápido do Office somente após confirmar impacto e janela de manutenção do usuário.
6. Se o incidente começou logo após update conhecido, registrar a versão exata para possível rollback centralizado.

## Validação
- Outlook abre em modo normal;
- mailbox principal sincroniza;
- add-ins críticos de negócio abrem sem travar;
- envio e recebimento funcionam;
- não há novo evento crítico no log após teste.

## Rollback
- reabilitar add-in desabilitado se ele não for a causa;
- restaurar perfil antigo caso novo perfil falhe;
- retornar nome original do OST se o rebuild não resolver.

## Quando escalar
- falha em múltiplas máquinas após o mesmo update;
- dependência de add-in corporativo sem owner disponível;
- suspeita de corrupção de mailbox no lado Exchange/Office 365;
- necessidade de rollback de versão Click-to-Run.

## Macro ITIL sugerida
"Validado comportamento do Outlook, testado modo seguro, revisados add-ins e perfil local. Aplicada ação controlada de isolamento de add-in/perfil/OST e validado retorno operacional do usuário."

## Riscos
- rebuild de OST força nova sincronização e pode consumir banda;
- desabilitar add-in pode impactar assinatura digital ou integrações fiscais;
- recriar perfil sem mapear caixas compartilhadas pode gerar falso negativo operacional.
