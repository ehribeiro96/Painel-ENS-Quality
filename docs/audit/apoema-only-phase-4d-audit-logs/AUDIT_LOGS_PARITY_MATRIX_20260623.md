# Audit Logs Parity Matrix — 2026-06-23

| Capacidade | /audit-logs legacy | Apoema Logs de Auditoria | Paridade | Observação |
|---|---|---|---|---|
| Rota protegida | sim | sim | sim | ambas exigem sessão válida |
| Lista/timeline de eventos | sim | sim | sim | cards de auditoria com paginação |
| Busca | sim | sim | sim | texto/busca e query na API |
| Filtros | sim | sim | sim | ação, entidade, IDs, fonte e datas |
| Ator/usuário | sim | sim | sim | `actor_id` e IDs relacionados |
| Ação/evento | sim | sim | sim | `action` exposto no card |
| Timestamp | sim | sim | sim | `created_at` exposto e formatado |
| Status/severidade | sim | sim | sim | badges de estado e fonte |
| Detalhe/contexto | sim | sim | sim | `before/after` preservados |
| Estado vazio | sim | sim | sim | empty state controlado |
| Loading/error | sim | sim | sim | loading e alertas explícitos |
| PT-BR | sim | sim | sim | textos e labels em português |
| Responsividade | sim | sim | sim | usa o mesmo sistema Base44 |
| Integração com backend | sim | sim | sim | `api.audit` real é usada |

## Política
`POLICY_A_SAFE_REDIRECT`

## Observação
`/audit-logs` pode redirecionar com segurança para `/apoema/audit-logs`, preservando compatibilidade e query string.
