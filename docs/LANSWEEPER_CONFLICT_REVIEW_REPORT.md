# Lansweeper Conflict Review Report

Data: 2026-06-03

## Resumo executivo

Import UAT analisado em modo somente leitura. Nenhum Apply foi executado e nenhum dado foi alterado.

Import ID: `bf8c7125-e0dc-4b9a-b46a-ac92bbd18b68`

Resultado do staging:

| Decisao | Linhas |
| --- | ---: |
| `CREATE` | 1693 |
| `CONFLICT` | 14 |
| `REVIEW_REQUIRED` | 2 |
| `SKIPPED_DUPLICATE_IN_FILE` | 6 |
| `INVALID` | 0 |

O endpoint de conflitos retornou 16 registros porque inclui os 14 conflitos bloqueantes e as 2 revisoes obrigatorias IP-only.

Decisao final: `NEEDS_SPREADSHEET_FIX`.

Motivo: os 14 conflitos representam colisao real de serial ou hostname. Alem disso, os 6 `SKIPPED_DUPLICATE_IN_FILE` nao sao todos duplicatas equivalentes operacionais; alguns carregam IP/tipo diferentes e precisam de revisao humana antes de qualquer apply completo.

## Arquivo auxiliar de correcao

Foi gerada uma planilha auxiliar para revisao humana dos grupos problematicos:

`uat_evidence/lansweeper_conflict_review/lansweeper_conflict_correction_template.xlsx`

Conteudo incluido:

- 14 linhas em `CONFLICTS`;
- 2 linhas em `REVIEW_REQUIRED`;
- 6 linhas em `SKIPPED_DUPLICATES`;
- lista controlada para `technician_decision`;
- recomendacao operacional preenchida por tipo de conflito.

Essa planilha nao altera o banco, nao altera a `Planilha.xlsx` original e nao autoriza Apply. Ela deve ser usada para registrar a decisao tecnica antes de corrigir a origem ou seguir para uma amostra controlada.

## Conflitos por categoria

| Categoria | Quantidade | Observacao |
| --- | ---: | --- |
| Serial duplicado com hostnames diferentes | 8 linhas / 4 grupos | Bloqueio real; corrigir planilha ou confirmar equipamento unico |
| Hostname duplicado com seriais diferentes | 4 linhas / 2 grupos | Mistura monitor + desktop com mesmo nome; precisa separar identidade |
| Identidade ambigua por hostname ja visto | 2 linhas / 2 grupos | Hostname colide com item anterior sem serial |
| IP-only / identidade fraca | 2 linhas | Revisao obrigatoria, sem virar hostname |
| Duplicata equivalente marcada como skipped | 6 linhas | Exige revisao; nem todas sao equivalentes |

## Tabela dos 14 conflitos bloqueantes

| Linha | Categoria | Chave envolvida | Hostname/Name | Serial | Type / Custom1 | Fabricante / Modelo | IP | Motivo | Recomendacao | Decisao operacional |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 82 | Serial duplicado | `CN-0M1VFN-74445-37V-AXMS` | `16836` | `CN-0M1VFN-74445-37V-AXMS` | Monitor / MONITOR | DELL / U2312HMT | - | Mesmo serial aparece tambem na linha 83 com hostname `16839`. | Verificar etiqueta/serial fisico. Manter uma linha ou corrigir serial/hostname. | Corrigir planilha |
| 83 | Serial duplicado | `CN-0M1VFN-74445-37V-AXMS` | `16839` | `CN-0M1VFN-74445-37V-AXMS` | Monitor / MONITOR | DELL / U2312HMT | - | Mesmo serial aparece tambem na linha 82 com hostname `16836`. | Verificar se e duplicidade de monitor ou erro de serial. | Corrigir planilha |
| 85 | Serial duplicado | `CN-0M1VFN-74445-37V-B15S` | `16848` | `CN-0M1VFN-74445-37V-B15S` | Monitor / MONITOR | DELL / U2312HMT | - | Mesmo serial aparece tambem na linha 87 com hostname `16854`. | Conferir inventario fisico; serial nao pode identificar dois ativos distintos. | Corrigir planilha |
| 87 | Serial duplicado | `CN-0M1VFN-74445-37V-B15S` | `16854` | `CN-0M1VFN-74445-37V-B15S` | Monitor / MONITOR | DELL / U2312HMT | - | Mesmo serial aparece tambem na linha 85 com hostname `16848`. | Conferir inventario fisico; manter apenas a linha correta. | Corrigir planilha |
| 471 | Serial duplicado | `FBLB2X3` | `22243` | `FBLB2X3` | Monitor / MONITOR | DELL / U2424H | - | Mesmo serial aparece tambem na linha 472 com hostname `22244`. | Validar serial no equipamento; corrigir duplicidade antes do apply. | Corrigir planilha |
| 472 | Serial duplicado | `FBLB2X3` | `22244` | `FBLB2X3` | Monitor / MONITOR | DELL / U2424H | - | Mesmo serial aparece tambem na linha 471 com hostname `22243`. | Validar se o serial foi copiado para o ativo errado. | Corrigir planilha |
| 1281 | Hostname duplicado | `RJM011HP` | `RJM011HP` | `BRC406008Z` | Monitor / MONITOR | HP / P22AG5 | - | Hostname `RJM011HP` tambem aparece na linha 1282 como DESKTOP com outro serial. | Monitor e desktop nao devem compartilhar hostname como identidade. Completar identificador do monitor ou separar nome. | Manter revisao |
| 1282 | Hostname duplicado | `RJM011HP` | `RJM011HP` | `BRJ436KQ6C` | Windows / DESKTOP | HP / HP PRO MINI 400 G9 DESKTOP PC | `192.168.0.115` | Mesmo hostname da linha 1281, mas outro serial e outra familia. | Preservar desktop com hostname; corrigir monitor para identidade propria. | Candidato a merge manual |
| 1283 | Hostname duplicado | `RJM012HP` | `RJM012HP` | `BRC406007Z` | Monitor / MONITOR | HP / P22AG5 | - | Hostname `RJM012HP` tambem aparece na linha 1284 como DESKTOP com outro serial. | Monitor e desktop precisam de identificadores distintos. | Manter revisao |
| 1284 | Hostname duplicado | `RJM012HP` | `RJM012HP` | `BRJ437KQVX` | Windows / DESKTOP | HP / HP PRO MINI 400 G9 DESKTOP PC | `192.168.0.63` | Mesmo hostname da linha 1283, mas outro serial e outra familia. | Preservar desktop com hostname; corrigir monitor para identidade propria. | Candidato a merge manual |
| 1387 | Identidade ambigua | `RJM21896` | `RJM21896` | `YL7W65H4MJ` | IOS / NOTEBOOK | MACBOOK / MACBOOK PRO 16.2 M1 MAX | `192.168.0.138` | Hostname `RJM21896` ja apareceu em linhas sem serial, tipo Network/NAS e IPs diferentes. | Nao aplicar automaticamente. Separar entradas de rede/NAS do notebook MacBook; confirmar qual item tem o hostname real. | Corrigir planilha |
| 1413 | Identidade ambigua | `RJM22135` | `RJM22135` | `9HJ4594` | Windows / DESKTOP | DELL / OPTIPLEX MICRO 7020 | `192.168.0.132` | Hostname `RJM22135` ja apareceu antes como NAS sem serial na linha 1412. | Confirmar se NAS e desktop sao o mesmo host ou registros distintos; nao mesclar sem evidencia. | Corrigir planilha |
| 1683 | Serial duplicado | `RZPB1J9001797` | `WE-007` | `RZPB1J9001797` | Wifi Extender / WIFI EXTENDER | D-LINK / DWA-131 | - | Mesmo serial aparece tambem na linha 1684 com hostname `WE-008`. | Validar serial fisico dos extensores; manter uma linha ou corrigir serial. | Corrigir planilha |
| 1684 | Serial duplicado | `RZPB1J9001797` | `WE-008` | `RZPB1J9001797` | Wifi Extender / WIFI EXTENDER | D-LINK / DWA-131 | - | Mesmo serial aparece tambem na linha 1683 com hostname `WE-007`. | Validar se dois extensores foram cadastrados com o mesmo serial. | Corrigir planilha |

## Revisao dos 2 `REVIEW_REQUIRED`

| Linha | Categoria | Chave | Name | Serial | Type / Custom1 | Modelo | IP | Motivo | Recomendacao |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 227 | IP-only | `source_external_key` | `192.168.3.43` | - | VOIP phone / vazio | PHONE2BUSINESS PH-301P 52.82.104.2 | `192.168.3.43` | Linha sem serial, patrimonio ou hostname confiavel. | Manter revisao. Completar identificador fisico/logico antes de aplicar como ativo final. |
| 228 | IP-only | `source_external_key` | `192.168.3.44` | - | VOIP phone / vazio | PHONE2BUSINESS PH-301P 52.82.104.2 | `192.168.3.44` | Linha sem serial, patrimonio ou hostname confiavel. | Manter revisao. Nao transformar IP em hostname. |

Confirmacao: os 2 `REVIEW_REQUIRED` sao os IP-only esperados. O pipeline preservou IP como `ip_address` e nao preencheu `hostname`.

## Revisao dos 6 `SKIPPED_DUPLICATE_IN_FILE`

| Linha skipped | Linha canonica | Identidade | Hostname | Tipo / familia | IP skipped | IP canonico | Avaliacao | Recomendacao |
| ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| 689 | 688 | hostname | `ANDROID-F253DA` | NAS / OTHER | `10.0.33.84` | `10.0.33.17` | Possivel duplicata, mas IP diverge. | Candidato a merge manual; confirmar se sao interfaces do mesmo equipamento. |
| 1146 | 1145 | hostname | `IFP7550-5.FUNENSEG.ORG` | NAS/OTHER vs Network device/NETWORK | `192.168.0.224` | `192.168.0.206` | Nao e duplicata perfeitamente equivalente; tipo e IP divergem. | Manter revisao ou corrigir origem. |
| 1383 | 1382 | hostname | `RJM21896` | Network device / NETWORK | `192.168.0.17` | `10.0.33.12` | Varios IPs para mesmo hostname sem serial. | Corrigir planilha; nao aceitar automaticamente. |
| 1384 | 1382 | hostname | `RJM21896` | Windows / OTHER | `192.168.0.17` | `10.0.33.12` | Tipo diverge de Network device; sem serial. | Corrigir planilha; nao aceitar automaticamente. |
| 1385 | 1382 | hostname | `RJM21896` | Network device / NETWORK | `192.168.0.19` | `10.0.33.12` | Mesmo hostname com IP diferente. | Corrigir planilha; nao aceitar automaticamente. |
| 1386 | 1382 | hostname | `RJM21896` | Network device / NETWORK | `192.168.0.32` | `10.0.33.12` | Mesmo hostname com IP diferente. | Corrigir planilha; nao aceitar automaticamente. |

Conclusao sobre skipped: nao confirmar os 6 como duplicatas equivalentes. Eles estao seguros porque foram pulados pelo pipeline, mas operacionalmente precisam de revisao. O grupo `RJM21896` deve ser corrigido antes de apply completo.

## Recomendacao operacional

1. Corrigir na planilha os 4 grupos de serial duplicado:
   - `CN-0M1VFN-74445-37V-AXMS`;
   - `CN-0M1VFN-74445-37V-B15S`;
   - `FBLB2X3`;
   - `RZPB1J9001797`.
2. Separar identidade de monitor e desktop nos pares:
   - `RJM011HP`;
   - `RJM012HP`.
3. Revisar manualmente os grupos:
   - `RJM21896`;
   - `RJM22135`;
   - `ANDROID-F253DA`;
   - `IFP7550-5.FUNENSEG.ORG`.
4. Manter `192.168.3.43` e `192.168.3.44` como revisao obrigatoria ou completar identificador antes de apply.
5. Nao executar apply completo enquanto os conflitos acima nao forem tratados.

## Decisao final

Decisao: `NEEDS_SPREADSHEET_FIX`.

Justificativa:

- Os 14 conflitos estao listados e explicados.
- Existem conflitos reais de serial e hostname.
- Os 6 skipped nao sao todos equivalentes do ponto de vista operacional.
- Os 2 review_required foram confirmados como IP-only.
- O pipeline nao abortou a importacao inteira e nao mascarou conflitos.
- Apply nao foi executado.

## Proximos passos

1. Corrigir a planilha ou produzir uma amostra controlada sem os grupos conflitantes.
2. Fazer novo upload para staging.
3. Confirmar que `CONFLICT=0` ou que os conflitos restantes foram aceitos por decisao humana documentada.
4. Fazer backup antes de qualquer apply.
5. Executar apply somente com autorizacao explicita.
