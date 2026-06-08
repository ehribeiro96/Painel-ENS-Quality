---
id: "rdp-entre-dominios-sem-trust"
title: "RDP entre domínios sem trust"
document_type: "decision_record"
domain: "rdp-vpn"
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
  - "rdp"
  - "vpn"
  - "domain"
  - "trust"
  - "credssp"
---

## Problema
Usuário precisa acessar via RDP um host em outro domínio sem relação de trust, frequentemente por VPN ou segmento isolado.

## Sintomas
- erro de credenciais mesmo com usuário correto;
- mensagem de que o logon não pôde ser concluído;
- host responde ping, mas sessão RDP falha;
- NLA ou CredSSP impedem autenticação cruzada.

## Perguntas mínimas
- Há conectividade IP e porta 3389 até o destino?
- O usuário usará conta local, conta do domínio remoto ou bastion?
- Existe jump server homologado?
- NLA está exigido no destino?

## Evidências necessárias
- print do erro;
- teste de reachability na VPN;
- método de autenticação esperado;
- nome do host sem dados sensíveis adicionais;
- owner do ambiente remoto.

## Comandos seguros
```powershell
Test-NetConnection HOST_DESTINO -Port 3389
cmdkey /list
```

```cmd
qwinsta /server:HOST_DESTINO
```

## Hipóteses
1. uso de credencial no formato incorreto;
2. NLA exigindo contexto não aceito;
3. ausência de rota ou ACL para 3389;
4. política local negando logon remoto;
5. cenário exige bastion ou jump box em vez de acesso direto.

## Resolução
1. Confirmar modelo de acesso homologado.
2. Testar reachability antes de discutir credencial.
3. Orientar formato de usuário apropriado, como `HOST\usuario_local` ou domínio remoto, quando permitido.
4. Se não houver trust, evitar suposições de SSO.
5. Confirmar com owner remoto se o host aceita aquele principal para logon remoto.
6. Priorizar jump server corporativo quando existir.

## Validação
- porta 3389 acessível;
- tela de login aceita o principal esperado;
- sessão abre com autorização formal;
- acesso fica reproduzível com método documentado.

## Rollback
- remover credenciais armazenadas indevidas com `cmdkey` se o teste gravar entrada incorreta;
- retornar ao método anterior de acesso homologado.

## Quando escalar
- necessidade de firewall ou ACL;
- política de acesso remoto entre domínios;
- host crítico ou ambiente segregado;
- dúvida sobre compliance do método.

## Macro ITIL sugerida
"Validado cenário de RDP sem trust, com foco em conectividade, método homologado de autenticação e necessidade de bastion, evitando alterações inseguras em NLA ou políticas de acesso."

## Riscos
- desabilitar NLA sem governança é inadequado;
- armazenar credencial errada gera ruído em testes;
- acesso direto pode violar desenho de segurança do ambiente.
