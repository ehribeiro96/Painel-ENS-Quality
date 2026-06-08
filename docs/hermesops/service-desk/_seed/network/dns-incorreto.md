---
id: "dns-incorreto"
title: "DNS incorreto causando falhas de domínio e aplicações"
document_type: "troubleshooting_note"
domain: "network"
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
  - "dns"
  - "name-resolution"
  - "ad"
  - "split-dns"
  - "vpn"
---

## Problema
Resolução DNS incorreta direciona a estação para servidores indevidos ou impede localização de recursos internos, controladores de domínio e aplicações corporativas.

## Sintomas
- navegação interna falha por nome, mas funciona por IP;
- login de domínio lento;
- GPO e mapeamentos não aplicam;
- aplicação resolve endereço público em vez de interno;
- VPN conecta, porém recursos internos não resolvem.

## Perguntas mínimas
- O DNS está obtido por DHCP, estático ou VPN?
- O problema ocorre só na VPN?
- O endpoint resolve nomes públicos e internos?
- Houve mudança recente de rede ou política?

## Evidências necessárias
- `ipconfig /all`;
- `nslookup` para nome interno e público;
- interface ativa;
- lista de servidores DNS configurados;
- horário e local do teste.

## Comandos seguros
```powershell
Get-DnsClientServerAddress
Resolve-DnsName servidor.interno.local -ErrorAction SilentlyContinue
Resolve-DnsName www.microsoft.com -ErrorAction SilentlyContinue
```

```cmd
ipconfig /all
nslookup servidor.interno.local
```

## Hipóteses
1. DNS público configurado manualmente;
2. DHCP entregando servidor errado;
3. VPN não aplicando split-DNS;
4. cache local com respostas antigas;
5. ordem de interfaces incorreta.

## Resolução
1. Confirmar baseline esperado de DNS para aquele cenário.
2. Comparar DNS ativo com rede, OU ou VPN esperada.
3. Corrigir origem da configuração, não apenas o sintoma local.
4. Limpar cache local somente após validar que a configuração já está correta.
5. Repetir testes de resolução para nomes internos e externos.

## Validação
- nomes internos resolvem para endereços corretos;
- GPO, login ou aplicação voltam a funcionar;
- DNS ativo corresponde ao baseline;
- reproduções posteriores mantêm resultado.

## Rollback
- reverter alteração manual de DNS se ela foi feita apenas para teste;
- restaurar escopo DHCP ou VPN anterior quando aplicável.

## Quando escalar
- escopo DHCP incorreto;
- VPN sem split-DNS;
- impacto em vários usuários;
- resolução errada envolvendo recurso crítico.

## Macro ITIL sugerida
"Identificada divergência de resolução DNS em relação ao baseline da rede, com correção orientada à origem da configuração e validação por resolução interna e externa."

## Riscos
- DNS manual pode esconder falha real de DHCP ou VPN;
- flush de cache antes da coleta reduz evidência;
- usar resolvedores públicos em ambiente AD quebra serviços dependentes.
