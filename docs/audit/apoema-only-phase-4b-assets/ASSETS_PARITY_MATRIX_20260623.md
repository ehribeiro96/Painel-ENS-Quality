# Assets Parity Matrix — 2026-06-23

Assets legacy -> Apoema Ativos

| Capacidade | /assets legacy | Apoema Ativos | Paridade | Observação |
|---|---|---|---|---|
| Rota protegida | sim | sim | sim | `/assets` agora redireciona para `/apoema/assets` sob `ProtectedRoute`. |
| Lista/tabela de ativos | sim | sim | sim | Legacy usa tabela operacional; Apoema usa `DataTable`. |
| Busca | sim | sim | sim | Ambas as superfícies permitem busca textual. |
| Filtros | sim | sim | sim | Legacy tem filtros avançados; Apoema tem busca e controle local de leitura. |
| Detalhes/side panel | sim | sim | sim | Legacy mostra detalhes no fluxo operacional; Apoema mantém sidebar de detalhes. |
| Status do ativo | sim | sim | sim | Ambas expõem status de forma explícita. |
| Localização/responsável | sim | sim | parcial | Legacy mostra campos operacionais completos; Apoema mostra localização e owner. |
| Patrimônio/serial/tag | sim | parcial | parcial | Legacy mantém a operação completa; Apoema prioriza identificação resumida. |
| Ações principais | sim | parcial | parcial | Legacy inclui criar/editar/mover/desativar; Apoema prioriza revisão. |
| Estado vazio | sim | sim | sim | Legacy e Apoema usam estados vazios explícitos. |
| Loading/error | sim | n/a | parcial | Apoema Ativos é estático e não depende de backend nesta etapa. |
| PT-BR | sim | sim | sim | Copy e navegação permanecem em PT-BR. |
| Responsividade | sim | sim | sim | O layout Apoema já foi ajustado para densidade responsiva. |
| Integração com backend | sim | não | parcial | O caminho legacy é backend-backed; Apoema é uma superfície local de operação. |

parity_minimum_met: true
policy: POLICY_A_SAFE_REDIRECT
