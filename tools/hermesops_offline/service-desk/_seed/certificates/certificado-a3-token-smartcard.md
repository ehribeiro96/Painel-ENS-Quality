---
id: "certificado-a3-token-smartcard"
title: "Certificado A3 em token ou smartcard não reconhecido"
document_type: "playbook"
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
  - "a3"
  - "token"
  - "smartcard"
  - "middleware"
---

## Problema
Token USB ou smartcard com certificado A3 não é reconhecido pela estação ou pela aplicação de assinatura.

## Sintomas
- dispositivo aparece sem driver adequado;
- PIN é solicitado, mas certificado não lista;
- aplicação fecha ao acessar módulo criptográfico;
- token funciona em outra máquina, mas não na atual.

## Perguntas mínimas
- O token funciona em outra estação homologada?
- Qual middleware ou driver está em uso?
- A falha começou após atualização de Windows ou middleware?
- O problema afeta apenas um leitor ou token?

## Evidências necessárias
- print do Gerenciador de Dispositivos;
- nome do middleware instalado;
- mensagem de erro da aplicação;
- confirmação de funcionamento em outra estação;
- data do último uso bem-sucedido.

## Comandos seguros
```powershell
Get-PnpDevice | Where-Object {$_.FriendlyName -match 'smart|token|reader'}
Get-Service SCardSvr
```

```cmd
certutil -scinfo
```

## Hipóteses
1. driver ou middleware incompatível;
2. serviço de smart card parado;
3. conflito entre versões de middleware;
4. token com falha física;
5. aplicação acessando CSP ou KSP incompatível.

## Resolução
1. Confirmar funcionamento físico do token ou leitor.
2. Validar serviço Smart Card em execução.
3. Identificar versão do middleware homologado.
4. Remover conflito entre middlewares concorrentes apenas sob procedimento aprovado.
5. Testar leitura com ferramenta nativa segura sem expor certificado.
6. Se o token funcionar em outra estação, focar em driver ou middleware local.

## Validação
- token é detectado pelo sistema;
- certificado aparece no utilitário ou aplicação-alvo;
- autenticação ou PIN ocorre sem travamento;
- assinatura de teste conclui.

## Rollback
- restaurar versão anterior do middleware caso a mudança recente tenha introduzido falha;
- reverter driver para baseline homologado da imagem corporativa.

## Quando escalar
- necessidade de fornecedor do certificado;
- suspeita de bloqueio ou falha física do token;
- conflito com aplicação fiscal proprietária;
- alteração em middleware com impacto amplo.

## Macro ITIL sugerida
"Executada análise de reconhecimento de token ou smartcard com validação de driver, serviço e middleware homologado, preservando material criptográfico e sem copiar conteúdo sensível."

## Riscos
- middleware errado pode derrubar outros certificados;
- múltiplos CSP ou KSP em paralelo causam falsos sintomas;
- coleta indevida de serials completos ou dumps do token é proibida.
