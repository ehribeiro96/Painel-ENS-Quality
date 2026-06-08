# Relatório de Execução UAT

Gerado em: 2026-06-02T12:13:53.1001994Z

## Resumo Executivo

Decisão recomendada: **GO COM RESSALVAS**

## Ambiente Testado

- SessionDir: `C:\Users\estevao.quality\Desktop\Assinatura + Ativos\uat_evidence\20260602_091209`
- Project name: `itam_uat_packaging`
- URL: `http://127.0.0.1:8080`
- Admin email: `estevao.quality@ens.edu.br`
- Backup inicial: `C:\Users\estevao.quality\Desktop\Assinatura + Ativos\backups\itam_backup_20260602_091229.manifest.json`
- Backup final: `C:\Users\estevao.quality\Desktop\Assinatura + Ativos\backups\itam_backup_20260602_091245.manifest.json`
- Regressão pós-UAT: `passed`

## Participantes

- Não informado no CSV.

## Cenários

- Total: 1
- Aprovados: 0
- Aprovados com ressalva: 0
- Reprovados: 0
- Observação: UAT incompleto ou CSV ainda sem decisões preenchidas.

## Bugs Por Severidade

- BLOCKER: 0
- CRITICAL: 0
- HIGH: 0
- MEDIUM: 0
- LOW: 0

## Bugs Por Área

- Nenhum bug aberto informado.

## BLOCKERs

- Nenhum.

## CRITICALs

- Nenhum.

## HIGHs

- Nenhum.

## MEDIUMs

- Nenhum.

## LOWs

- Nenhum.

## Evidências

- Evidências não informadas no CSV.

## Resultado Pós-UAT

- `/health`: 200
- `/`: 200
- `/assinaturas/`: 200
- `/admin/`: 302
- `/api/v1/assets`: 401

## Decisão Recomendada

**GO COM RESSALVAS**

Critério aplicado: NO-GO para BLOCKER/CRITICAL abertos ou falha em fluxo crítico; GO COM RESSALVAS para HIGH/MEDIUM documentados; GO quando não há BLOCKER/CRITICAL/HIGH abertos e fluxos críticos aprovados.
