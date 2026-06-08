---
id: "gpo-nao-aplica"
title: "GPO não aplica no endpoint ou usuário"
document_type: "kcs_article"
domain: "gpo-ad"
status: "draft"
risk_level: "medium"
owner: "Service Desk N2"
source_type: "internal_seed"
sensitivity: "sanitized"
automation_allowed: false
requires_admin: true
external_model_allowed: true
last_review: "2026-06-07"
version: 1
tags:
  - "gpo"
  - "ad"
  - "ou"
  - "gpresult"
  - "sysvol"
---

## Problema
Política de Grupo esperada não é aplicada ao computador ou ao usuário, causando ausência de configurações como impressoras, certificados, scripts ou restrições visuais.

## Sintomas
- papel de parede, mapeamento ou política de segurança não aparecem;
- `gpresult` não lista a GPO esperada;
- evento de GroupPolicy mostra erro de acesso, filtragem ou timeout;
- usuário em OU correta, mas sem resultado esperado.

## Perguntas mínimas
- A falha é por usuário, computador ou ambos?
- O objeto está na OU correta?
- Existe filtro WMI, security filtering ou loopback?
- O problema começou após mudança em AD ou SYSVOL?

## Evidências necessárias
- resultado de `gpresult /h` ou `/r`;
- nome da GPO esperada;
- OU do objeto;
- hora do último logon;
- Event IDs de GroupPolicy.

## Comandos seguros
```cmd
gpresult /r
gpupdate /force
whoami /groups
```

```powershell
Get-WinEvent -LogName System -MaxEvents 50 | Where-Object {$_.ProviderName -like '*GroupPolicy*'}
```

## Hipóteses
1. objeto em OU incorreta;
2. security filtering excluindo usuário ou computador;
3. filtro WMI incompatível;
4. SYSVOL ou replicação inconsistente;
5. problema de DNS ou linha de visão ao controlador.

## Resolução
1. Confirmar escopo correto da GPO e OU do objeto.
2. Revisar `gpresult` para identificar negação por filtro de segurança ou WMI.
3. Validar se há conectividade e resolução de nome para domínio e DC.
4. Forçar atualização de política apenas para reproduzir, não como solução única.
5. Se houver indício de SYSVOL ou replicação, escalar para AD.
6. Se a política distribui certificados ou drive mappings, validar dependências associadas.

## Validação
- `gpresult` passa a listar a GPO esperada;
- efeito prático da política aparece;
- eventos de GroupPolicy deixam de registrar erro;
- reprodução em novo logon confirma persistência da correção.

## Rollback
- remover alteração de escopo recém-feita se a GPO afetar público indevido;
- desfazer teste em link de GPO ou security filtering caso gere impacto lateral.

## Quando escalar
- suspeita de replicação AD ou SYSVOL;
- GPO de segurança crítica;
- problema generalizado em múltiplos sites;
- necessidade de alteração em produção sem owner da política.

## Macro ITIL sugerida
"Analisada cadeia de aplicação de GPO com foco em OU, filtros, eventos e conectividade ao domínio. Correção aplicada ou escalonamento realizado conforme camada responsável."

## Riscos
- alteração precipitada em security filtering pode ampliar impacto;
- `gpupdate /force` sozinho mascara causa raiz;
- troubleshooting sem validar DNS ou DC pode gerar falso diagnóstico.
