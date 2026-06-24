# Stock Parity Matrix — 2026-06-23

Policy: POLICY_A_SAFE_REDIRECT
Target: /apoema/stock
Legacy alias: /stock

| Capacidade | /stock legacy | Apoema Estoque | Paridade | Observação |
|---|---|---|---|---|
| Rota protegida | Sim | Sim | Sim | Ambas ficam atrás de ProtectedRoute / ApoemaRoute. |
| Lista/tabela de estoque | Visão operacional resumida | Painel operacional Apoema | Parcial | A superfície foi consolidada em cards e resumo operacional. |
| Busca | Não evidenciado na superfície legacy | Não evidenciado | Parcial | O foco é paridade mínima com leitura real da API. |
| Filtros | Não evidenciado na superfície legacy | Não evidenciado | Parcial | Não houve regressão de filtros porque a experiência anterior já era simples. |
| Quantidade/saldo | Sim | Sim | Sim | Vem de `assetsByStatus`. |
| Status baixo/crítico | Sim | Sim | Sim | Indicadores por status mantidos. |
| Localização | Não evidenciado | Não evidenciado | Parcial | Não é superfície de localização detalhada. |
| Entrada/saída/movimentação | Não evidenciado | Não evidenciado | Parcial | Movimento permanece no fluxo de ativos, não no resumo de estoque. |
| Ações principais | Navegação operacional | Navegação operacional | Sim | Mantida leitura consultiva sem mock. |
| Estado vazio | Sim | Sim | Sim | `Base44EmptyState` preservado. |
| Loading/error | Sim | Sim | Sim | Estados explícitos preservados. |
| PT-BR | Sim | Sim | Sim | Textos em português. |
| Responsividade | Sim | Sim | Sim | Usa as superfícies Apoema. |
| Integração com backend | Sim | Sim | Sim | Usa API real de ativos por status. |
