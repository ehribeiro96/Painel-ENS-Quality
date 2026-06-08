# Lansweeper Import Fix Report

Data: 2026-06-03

## Problema

A planilha real do Lansweeper ainda gerava erros porque linhas com `Name` em formato de IP, nomes genericos ou identidade fraca eram tratadas como erro invalido ou podiam virar hostname indevido.

Arquivo analisado localmente:

`c:\Users\estevao.quality\Desktop\Planilha.xlsx`

Aba: `report`

## Causa raiz

- `Name` IP era removido de `hostname`, corretamente, mas a linha ficava sem identidade e caia em `missing_identity`.
- Nomes genericos podiam ser usados como identidade forte.
- `66` precisava ser tratado como placeholder nulo conforme regra atual da planilha real.
- O apply ainda bloqueava linhas seguras quando havia linhas apenas de revisao obrigatoria.

## Solucao aplicada

- `Name` com IP nao preenche `hostname`; preenche `ip_address`.
- Linhas sem serial/patrimonio/hostname recebem `source_external_key` no payload normalizado e em `source_metadata`.
- Identidade fraca por `source_external_key` vira `REVIEW_REQUIRED`, nao `INVALID`.
- Nomes genericos como `login`, `logon`, `404 - not found` e `msg_login_page_title` nao viram hostname confiavel.
- `66`, `Undefined`, `Not scanned` e vazios sao normalizados como `null`.
- `lastuser` segue apenas em `source_metadata.imported_user_hint`.
- Apply parcial foi ajustado:
  - conflitos reais continuam bloqueando;
  - linhas em revisao sao puladas;
  - linhas seguras podem ser aplicadas parcialmente.

## Diagnostico local da planilha corrigida

Sem upload/apply, usando o normalizador corrigido:

| Metrica | Valor |
| --- | ---: |
| Linhas | 1715 |
| Colunas | 56 |
| Preset | Lansweeper Assets Export |
| Barcode mapeado como patrimonio | Nao |
| Seriais validos | 1046 |
| Hostnames confiaveis | 1713 |
| Sem patrimonio | 1715 |
| Hints de usuario | 273 |
| IP/source-key fraco para revisao | 2 |
| CREATE | 1693 |
| REVIEW_REQUIRED | 2 |
| CONFLICT | 14 |
| SKIPPED_DUPLICATE_IN_FILE | 6 |

Principais motivos explicados:

- `weak_source_external_identity`;
- `skipped_duplicate_in_file`;
- `duplicate_in_file`;
- `serial_hostname_divergence`;
- `hostname_serial_divergence`.

Casos confirmados:

- `192.168.3.43` e `192.168.3.44` foram normalizados como `ip_address`, com `hostname=null`.
- 4 grupos de serial duplicado aparecem como conflito real.
- `RJM21896` aparece em 6 ocorrencias e fica explicado no relatorio de conflitos/revisoes.
- `RJM011HP` e `RJM012HP` sao classificados pelo `Custom1=MONITOR`, nao por `Type=Windows`.
- `lastuser` foi preservado apenas como `source_metadata.imported_user_hint`.
- `Barcode` 100% vazio gerou warning e nao virou patrimonio.

## Testes

- Adicionados testes para:
  - `Name` IP nao virar hostname;
  - IP-only virar `source_external_key` e `REVIEW_REQUIRED`;
  - hostname generico nao virar identidade forte;
  - `66` virar nulo globalmente;
  - linhas `REVIEW_REQUIRED` nao bloquearem apply parcial.
  - fixture sintetica `lansweeper_corrected_shape.xlsx` com 56 colunas e casos da planilha corrigida.
  - `PageParams(page_size=200)` para staging paginado sem erro 500.

## Validacao UAT da planilha corrigida

Backup criado antes do upload:

`backups\itam_backup_20260603_095548.dump`

Upload UAT executado sem apply:

- arquivo: `c:\Users\estevao.quality\Desktop\Planilha.xlsx`;
- import id: `bf8c7125-e0dc-4b9a-b46a-ac92bbd18b68`;
- status: `REVIEW_REQUIRED`;
- preview: `200`;
- staging `page_size=50`: `200`;
- staging `page_size=200`: `200`;
- conflitos: `200`;
- erros de validacao: `200`;
- report: `200`.

Resultado UAT:

| Metrica | Valor |
| --- | ---: |
| Total de linhas | 1715 |
| Linhas validas/seguras | 1693 |
| Linhas invalidas | 0 |
| Conflitos bloqueantes | 14 |
| Revisao obrigatoria | 2 |
| Duplicatas equivalentes puladas | 6 |
| `can_apply` | `false` |

O apply nao foi executado. O status `REVIEW_REQUIRED` e esperado porque ainda existem conflitos reais que precisam de decisao humana.

## Correcao adicional de staging

Durante a validacao UAT, `GET /api/v1/imports/{id}/staging?page_size=200` retornou `500` porque `PageParams` limitava `page_size` a `100`, enquanto a rota de staging permite `200`.

Correcao:

- `PageParams.page_size` agora aceita ate `200`;
- teste de regressao adicionado;
- endpoint validado em UAT com `200` itens retornados.

## Riscos restantes

- `source_external_key` ainda nao e coluna persistida em `assets`; fica em staging/report. Para reconciliacao futura robusta, recomenda-se migration conservadora.
- Conflitos reais da planilha corrigida continuam exigindo revisao humana antes do apply.
- A planilha corrigida completa nao foi aplicada nesta rodada.

## Proximos passos

- Fazer upload UAT da planilha corrigida para revisar staging e conflitos.
- Corrigir manualmente ou aceitar politicas para os 14 conflitos antes do apply.
- Avaliar coluna persistente `assets.source_external_key` em migration futura.
