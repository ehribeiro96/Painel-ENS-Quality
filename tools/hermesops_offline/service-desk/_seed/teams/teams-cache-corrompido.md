---
id: "teams-cache-corrompido"
title: "Teams com cache corrompido ou loop de autenticação"
document_type: "playbook"
domain: "teams"
status: "draft"
risk_level: "low"
owner: "Service Desk N2"
source_type: "internal_seed"
sensitivity: "sanitized"
automation_allowed: false
requires_admin: false
external_model_allowed: true
last_review: "2026-06-07"
version: 1
tags:
  - "teams"
  - "cache"
  - "login"
  - "webview2"
  - "m365"
---

## Problema
Microsoft Teams clássico ou novo Teams não inicia corretamente, entra em loop de login ou mostra interface em branco por corrupção de cache local.

## Sintomas
- tela branca ou preta;
- loop de autenticação;
- Teams abre e fecha;
- notificações não chegam;
- nova versão abre, mas não carrega chats ou calendário.

## Perguntas mínimas
- É Teams clássico ou novo Teams?
- O problema ocorre após troca de senha ou MFA?
- O Teams Web funciona no navegador?
- O usuário está em VPN ou rede interna com proxy?

## Evidências necessárias
- print da tela;
- confirmação de funcionamento do Teams Web;
- horário exato da última tentativa;
- versão do cliente;
- presença de múltiplas contas conectadas.

## Comandos seguros
```powershell
Get-Process ms-teams, teams -ErrorAction SilentlyContinue
Get-ChildItem "$env:APPDATA\Microsoft\Teams" -ErrorAction SilentlyContinue
Get-ChildItem "$env:LOCALAPPDATA\Packages\MSTeams*" -ErrorAction SilentlyContinue
```

## Hipóteses
1. cache corrompido;
2. token local inconsistente após troca de senha;
3. WebView2 com falha;
4. conflito entre conta pessoal e corporativa;
5. política de proxy bloqueando bootstrap.

## Resolução
1. Encerrar processos do Teams.
2. Identificar variante do cliente.
3. Renomear diretórios de cache local em vez de apagar permanentemente.
4. Reabrir Teams e refazer login corporativo.
5. Confirmar que o Teams Web funciona para isolar falha local.
6. Se persistir, validar runtime WebView2 e política de proxy do endpoint.

## Validação
- login concluído sem loop;
- chats e calendário carregam;
- busca de usuários funciona;
- chamada de teste abre dispositivos;
- não há novo diretório de erro recorrente após recriação do cache.

## Rollback
- restaurar pasta de cache renomeada para comparação;
- retornar ao cliente anterior se houver fallback operacional documentado pelo workplace.

## Quando escalar
- Teams Web também falha;
- múltiplos usuários na mesma unidade ou proxy com mesmo sintoma;
- falha de WebView2 administrado por imagem corporativa;
- suspeita de incidente Microsoft 365.

## Macro ITIL sugerida
"Realizada limpeza controlada de cache do Teams, validado teste web e reautenticação corporativa. Cliente voltou a carregar conversas e calendário sem perda de credenciais sensíveis."

## Riscos
- remoção incorreta de diretórios pode eliminar preferências locais;
- usuário com várias contas pode reconectar a conta errada;
- confundir cliente clássico com novo Teams leva a limpeza ineficaz.
