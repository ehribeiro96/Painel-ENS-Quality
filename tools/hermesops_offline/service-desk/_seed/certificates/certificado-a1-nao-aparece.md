---
id: "certificado-a1-nao-aparece"
title: "Certificado A1 não aparece para aplicação do usuário"
document_type: "troubleshooting_note"
domain: "certificates"
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
  - "certificado"
  - "a1"
  - "certmgr"
  - "store"
  - "assinatura"
---

## Problema
Aplicação fiscal, navegador ou assinador não enxerga certificado A1 esperado no repositório do usuário ou computador.

## Sintomas
- certificado não aparece na lista de seleção;
- assinador informa ausência de certificado válido;
- certificado aparece em um aplicativo e não em outro;
- cadeia ou validade não é reconhecida.

## Perguntas mínimas
- O certificado foi importado para usuário atual ou computador local?
- O problema ocorre em todos os aplicativos ou apenas um?
- O certificado está dentro da validade?
- Houve troca de perfil Windows ou perfil do navegador?

## Evidências necessárias
- nome amigável do certificado sem expor número completo;
- store onde ele deveria estar;
- validade;
- aplicação afetada;
- captura da tela de seleção vazia.

## Comandos seguros
```powershell
Get-ChildItem Cert:\CurrentUser\My
Get-ChildItem Cert:\LocalMachine\My
certmgr.msc
```

## Hipóteses
1. importação em store incorreto;
2. perfil do usuário diferente;
3. cadeia intermediária ausente;
4. aplicação 32-bit consultando contexto diferente;
5. certificado expirado ou com chave não acessível.

## Resolução
1. Confirmar store esperado da aplicação.
2. Validar presença do certificado sem copiar conteúdo sensível.
3. Se estiver no store errado, orientar reimportação controlada pelo responsável, sem exportar chave privada.
4. Validar cadeia de confiança e horário da estação.
5. Em aplicativo específico, testar execução no contexto correto do usuário.

## Validação
- certificado aparece na seleção da aplicação;
- assinatura de teste é concluída;
- validade e cadeia estão reconhecidas;
- comportamento é reproduzível após reabrir o sistema alvo.

## Rollback
- remover importação incorreta feita apenas para teste;
- retornar ao store original documentado se mudança de contexto causar conflito.

## Quando escalar
- suspeita de problema na mídia original do certificado;
- necessidade de reemissão;
- aplicação proprietária com consulta não padrão ao store;
- risco de exposição de chave privada.

## Macro ITIL sugerida
"Validado repositório lógico do certificado A1, visibilidade por contexto do usuário e cadeia de confiança, sem manipulação de material sensível fora do procedimento aprovado."

## Riscos
- qualquer exportação de chave privada foge do escopo desta fase;
- confundir CurrentUser com LocalMachine gera retrabalho;
- registrar serial completo ou arquivo original no corpus é proibido.
