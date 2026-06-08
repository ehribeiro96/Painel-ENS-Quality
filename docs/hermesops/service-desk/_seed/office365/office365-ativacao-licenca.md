---
id: "office365-ativacao-licenca"
title: "Office 365 sem ativar licença no desktop"
document_type: "kcs_article"
domain: "office365"
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
  - "office365"
  - "activation"
  - "license"
  - "signin"
  - "subscription"
---

## Problema
Aplicativos do Microsoft 365 Apps entram em modo somente leitura ou pedem ativação apesar de o usuário possuir licença atribuída.

## Sintomas
- banner de ativação pendente;
- Word ou Excel abre em modo reduzido;
- troca de senha recente gera pedido de login recorrente;
- conta antiga permanece vinculada no Office.

## Perguntas mínimas
- A licença foi atribuída e propagada no tenant?
- O usuário consegue entrar no portal web do Microsoft 365?
- Há mais de uma conta Office no dispositivo?
- O equipamento respeita o limite de ativações do usuário?

## Evidências necessárias
- print do banner de ativação;
- confirmação de acesso ao portal;
- licença atribuída pelo time responsável;
- nome da conta exibida no Office;
- horário da última tentativa.

## Comandos seguros
```powershell
Get-Process WINWORD, EXCEL, OUTLOOK -ErrorAction SilentlyContinue
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Office\Licenses" -ErrorAction SilentlyContinue
```

## Hipóteses
1. token de ativação desatualizado;
2. conta errada conectada;
3. licença ainda não propagada;
4. limite de instalações;
5. cache local de identidade corrompido.

## Resolução
1. Validar licença no lado administrativo antes de alterar o cliente.
2. Confirmar login web bem-sucedido com a conta corporativa correta.
3. Desconectar contas indevidas do Office.
4. Forçar nova autenticação do pacote local.
5. Se o cache de ativação estiver corrompido, recriar somente os artefatos locais de licença ou identidade de forma controlada.

## Validação
- aplicativos saem do modo somente leitura;
- banner de ativação desaparece;
- conta correta aparece em Arquivo > Conta;
- usuário cria e salva documento normalmente.

## Rollback
- reconectar conta anterior se a intervenção local tiver removido contexto necessário;
- restaurar fluxo de ativação anterior documentado pelo workplace.

## Quando escalar
- licença não atribuída no tenant;
- incidente Microsoft 365;
- limite de ativação exige ação administrativa;
- múltiplos usuários no mesmo lote de imagem.

## Macro ITIL sugerida
"Validada atribuição de licença Microsoft 365 e contexto de autenticação local do Office, com reautenticação controlada para restabelecer ativação do desktop."

## Riscos
- remover conta errada pode afetar OneDrive e Outlook;
- agir no cliente antes de confirmar a licença no tenant gera retrabalho;
- limpar artefatos de ativação sem critério pode exigir novo onboarding.
