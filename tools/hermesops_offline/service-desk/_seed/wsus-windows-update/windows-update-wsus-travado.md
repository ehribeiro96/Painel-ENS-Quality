---
id: "windows-update-wsus-travado"
title: "Windows Update apontando para WSUS travado"
document_type: "playbook"
domain: "wsus-windows-update"
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
  - "wsus"
  - "windows-update"
  - "gpo"
  - "bits"
  - "usosvc"
---

## Problema
Endpoint corporativo não recebe ou não instala atualizações quando configurado para WSUS, permanecendo em estado de verificação infinita, download travado ou erro de detecção.

## Sintomas
- tela de Windows Update fica em checking por longos períodos;
- código de erro recorrente em Settings;
- serviço UsoSvc ou wuauserv reinicia;
- máquina não reporta compliance esperado;
- `gpresult` mostra política WSUS aplicada, porém sem comunicação efetiva.

## Perguntas mínimas
- A máquina está na rede corporativa ou VPN com reachability ao WSUS?
- O problema afeta uma OU inteira ou apenas um host?
- Houve troca de GPO ou URL de WSUS recentemente?
- O usuário possui janela para reinício, se necessário?

## Evidências necessárias
- print da tela de update;
- resultado de `gpresult /r`;
- estado dos serviços de update;
- data/hora da última instalação bem-sucedida;
- nome da OU e política aplicada.

## Comandos seguros
```powershell
Get-Service wuauserv, usosvc, bits
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate' -ErrorAction SilentlyContinue
UsoClient StartScan
```

```cmd
gpresult /r
```

## Hipóteses
1. URL de WSUS inválida ou inacessível;
2. política parcialmente aplicada;
3. cache local de update inconsistente;
4. BITS parado;
5. TLS ou inspeção de rede interferindo na comunicação interna.

## Resolução
1. Confirmar se política WSUS está aplicada e coerente.
2. Validar serviços essenciais ativos.
3. Reaplicar GPO antes de qualquer limpeza mais invasiva.
4. Em janela aprovada e com privilégio adequado, resetar componentes de update somente de forma controlada e documentada.
5. Testar novo scan e registrar resultado.
6. Se o problema for coletivo, tratar como incidente de infraestrutura e não como endpoint isolado.

## Validação
- `gpresult` mantém política correta;
- serviço BITS e wuauserv estáveis;
- novo scan conclui sem loop;
- endpoint volta a listar updates aprovados ou reporta sem erro;
- data de último scan ou instalação evolui.

## Rollback
- restaurar configuração padrão de política previamente registrada;
- reverter alterações manuais em serviços ou cache se houver desvio do baseline corporativo.

## Quando escalar
- falha em massa por OU ou site;
- suspeita de indisponibilidade do WSUS;
- endpoint crítico com update de segurança atrasado;
- necessidade de ação administrativa fora da autonomia do N2.

## Macro ITIL sugerida
"Validada aplicação de políticas WSUS, serviços de atualização e capacidade de novo scan. Ação executada em modo controlado, com foco em restaurar conformidade sem burlar baseline corporativo."

## Riscos
- reset indevido pode apagar histórico de troubleshooting;
- intervenção fora de janela pode disparar reinícios;
- tratar falha de infraestrutura como caso unitário atrasa resposta ao incidente.
