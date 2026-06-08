---
id: "lentidao-windows"
title: "Lentidão generalizada no Windows"
document_type: "kcs_article"
domain: "windows"
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
  - "windows"
  - "performance"
  - "disk"
  - "cpu"
  - "startup"
---

## Problema
Estação apresenta lentidão perceptível no login, abertura de aplicativos ou uso geral do sistema operacional.

## Sintomas
- login demora vários minutos;
- disco em 100 por cento;
- aplicações simples travam;
- Explorer reinicia;
- problema piora após boot ou update.

## Perguntas mínimas
- A lentidão é constante ou intermitente?
- Começou após update, instalação ou mudança de perfil?
- Afeta só um usuário?
- Há pouco espaço em disco?

## Evidências necessárias
- uso de CPU, memória e disco;
- espaço livre;
- lista de processos de maior consumo;
- horário em que a lentidão é mais forte;
- presença de scans ou updates em execução.

## Comandos seguros
```powershell
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
Get-PSDrive -PSProvider FileSystem
Get-Counter '\PhysicalDisk(_Total)\% Disk Time'
```

## Hipóteses
1. disco degradado ou saturado;
2. startup excessivo;
3. update ou antivírus em execução;
4. perfil corrompido;
5. memória insuficiente.

## Resolução
1. Identificar gargalo dominante.
2. Remover percepção subjetiva usando medição simples.
3. Se o problema for pós-boot, revisar itens de inicialização e scans.
4. Se houver pouco espaço, tratar housekeeping permitido.
5. Se houver indício de hardware, abrir trilha específica.

## Validação
- tempo de resposta melhora;
- uso de disco ou CPU retorna ao normal;
- aplicativo crítico abre dentro do aceitável;
- usuário confirma melhora perceptível.

## Rollback
- restaurar item de inicialização desabilitado se ele não era causa;
- desfazer alteração de tuning não padronizada.

## Quando escalar
- suspeita de hardware ou SSD;
- consumo anômalo de processo corporativo;
- imagem base degradada em lote;
- lentidão acompanhada de alertas de segurança.

## Macro ITIL sugerida
"Lentidão analisada por métrica objetiva de CPU, disco, memória e espaço, com mitigação direcionada ao gargalo predominante e validação funcional junto ao usuário."

## Riscos
- encerrar processo sem análise pode agravar o quadro;
- tuning fora do baseline dificulta suporte futuro;
- focar só em CPU pode perder gargalo de disco.
