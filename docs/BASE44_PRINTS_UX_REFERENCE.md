# Base44 e Prints como Referencia UX

Data: 2026-06-02

## Decisao

Os prints enviados pelo usuario sao a referencia visual oficial para alinhamento
UX/UI desta rodada.

O diretorio `frontend/legacy/Base44` nao esta confirmado como sendo o mesmo
material dos prints. Ele nao deve ser usado como fonte oficial de regra de
negocio, dados, importacao, autenticacao ou auditoria.

## Classificacao

| Item | Classificacao | Decisao |
|---|---|---|
| Prints enviados pelo usuario | UX_REFERENCE_FROM_PRINTS | Usar como referencia visual. |
| `frontend/itam-platform` | ACTIVE_RUNTIME | Frontend oficial React + Vite. |
| `frontend/legacy/Base44` | ARCHIVE_CANDIDATE | Prototipo antigo fora do runtime ativo; arquivado em quarentena. |
| `/assinaturas/` e `/admin/` | LEGACY_SUPPORTED | Legado Flask preservado. |

## Aplicacao pratica

A UI ativa foi ajustada para se aproximar dos prints em:

- sidebar escura com identidade Funenseg / Inventario TI;
- menu Dashboard, Ativos, Colaboradores, Atribuicoes, Auditoria e Importar/Exportar;
- rodape com usuario logado, perfil e sair;
- dashboard com cards, paineis e acoes rapidas;
- tela Importar/Exportar com card de upload e exportacao sinalizada.

## Regras preservadas

- Nenhum dado mockado foi introduzido.
- O pipeline real de importacao foi preservado.
- Nenhuma logica do Base44 foi copiada.
- APIs reais do sistema continuam sendo usadas.

## Validacao visual conservadora

Data: 2026-06-02

Foi executada uma rodada de QA visual em navegador Chromium controlado por CDP
contra o frontend Vite buildado/previewado localmente. Para nao alterar dados
UAT e nao depender de credenciais reais nesta rodada visual, as respostas de API
foram interceptadas apenas no navegador de QA com dados minimos controlados.
O codigo de produto permanece consumindo o client HTTP e as APIs reais.

Telas validadas:

- Dashboard (`/`)
- Ativos (`/assets`)
- Colaboradores (`/users`)
- Atribuicoes (`/assignments`)
- Auditoria (`/audit-logs`)
- Importar/Exportar (`/imports`)

Matrizes validadas:

- 1920x1080 em zoom 100%
- 1366x768 em zoom 100%
- 1366x768 com zoom simulado de 125%

Achados e ajustes:

- Foi identificado overflow horizontal em 1366x768 e em 1366x768 com zoom 125%
  nas telas mais densas.
- Foram aplicados ajustes pontuais de CSS responsivo em `styles.css` para:
  - limitar largura maxima de paineis e tabelas;
  - permitir grids quebrarem em duas colunas em viewports menores;
  - evitar crescimento minimo indevido de cards, filtros e conteudo principal;
  - preservar rolagem vertical sem criar overflow horizontal de pagina.
- A tela Importar/Exportar manteve estados vazios do pipeline como informacao
  honesta quando nao ha registros carregados.
- O botao de exportacao permaneceu desabilitado quando a funcionalidade nao esta
  disponivel, evitando label enganoso.

Resultado final:

- Nenhuma tela validada apresentou overflow horizontal apos os ajustes.
- Nenhuma sobreposicao visual foi detectada pela verificacao automatizada.
- Nao houve criacao de feature nova.
- Nao houve alteracao em backend, migrations, regra de negocio ou pipeline de
  importacao.

Evidencias geradas localmente:

- `uat_evidence/visual-qa/1920x1080-dashboard.png`
- `uat_evidence/visual-qa/1920x1080-assets.png`
- `uat_evidence/visual-qa/1920x1080-users.png`
- `uat_evidence/visual-qa/1920x1080-assignments.png`
- `uat_evidence/visual-qa/1920x1080-audit-logs.png`
- `uat_evidence/visual-qa/1920x1080-imports.png`
- `uat_evidence/visual-qa/1366x768-dashboard.png`
- `uat_evidence/visual-qa/1366x768-assets.png`
- `uat_evidence/visual-qa/1366x768-users.png`
- `uat_evidence/visual-qa/1366x768-assignments.png`
- `uat_evidence/visual-qa/1366x768-audit-logs.png`
- `uat_evidence/visual-qa/1366x768-imports.png`
- `uat_evidence/visual-qa/1366x768-zoom125-dashboard.png`
- `uat_evidence/visual-qa/1366x768-zoom125-assets.png`
- `uat_evidence/visual-qa/1366x768-zoom125-users.png`
- `uat_evidence/visual-qa/1366x768-zoom125-assignments.png`
- `uat_evidence/visual-qa/1366x768-zoom125-audit-logs.png`
- `uat_evidence/visual-qa/1366x768-zoom125-imports.png`
- `uat_evidence/visual-qa/visual-qa-results.json`

Risco restante:

- Ainda e recomendada uma validacao manual final contra o ambiente UAT real com
  login, dados reais de homologacao e permissoes reais, pois esta rodada foi
  restrita a QA visual e nao alterou dados UAT.
