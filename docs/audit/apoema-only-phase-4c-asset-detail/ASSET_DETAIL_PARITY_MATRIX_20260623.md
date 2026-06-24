# Asset Detail Parity Matrix — 2026-06-23

Asset Detail legacy -> Apoema Detalhe de Ativo

| Capacidade | /assets/:id legacy | Apoema Detalhe | Paridade | Observação |
|---|---|---|---|---|
| Rota protegida | sim | sim | sim | Mantida via `ProtectedRoute`. |
| URL direta por ID | sim | sim | sim | `/assets/:id` redireciona para `/apoema/assets/:id`. |
| Dados principais do ativo | sim | sim | sim | Headline, status e identificadores são carregados no detalhe. |
| Patrimônio/serial/tag | sim | sim | parcial | Patrimônio e serial são exibidos; tag depende da origem do dado. |
| Status | sim | sim | sim | Badge e resumo operacional permanecem explícitos. |
| Responsável/localização | sim | sim | sim | Campos principais seguem visíveis. |
| Histórico/movimentações | sim | sim | sim | Timeline e estado de carregamento preservados. |
| Ações principais | sim | sim | sim | Movimentar, consultar histórico e copiar resumo. |
| Copiar/gerar macro | sim | sim | sim | O fluxo de movimentação mantém macro assistida. |
| Loading/error/empty | sim | sim | sim | Estados controlados no detalhe canônico. |
| Voltar para lista | sim | sim | sim | `Link` relativo retorna para a lista de ativos. |
| PT-BR | sim | sim | sim | Copy permanece em português. |
| Responsividade | sim | sim | sim | A superfície usa a composição responsiva do Apoema. |
| Integração com backend | sim | sim | sim | O detalhe usa a API existente sem alterar contratos. |

parity_minimum_met: true
policy: POLICY_A_SAFE_DYNAMIC_REDIRECT
