# Future Removal Roadmap — Apoema-only

## Fase 5B — Remover aliases mortos somente se todos os redirects estiverem cobertos por testes
## Fase 5C — Remover componentes legacy não roteados
## Fase 5D — Reduzir AppShell legado
## Fase 5E — Isolar ou remover CSS legacy
## Fase 5F — Auditoria visual final
## Fase 5G — Checklist pré-push final

| Fase | Ação | Pré-requisito | Risco | Validação |
|---|---|---|---|---|
| 5B | Remover aliases `/ai-chat`, `/assets`, `/audit-logs`, `/imports`, `/macros`, `/stock`, `/signatures`, `/assignments`, `/users`, `/settings` | Contratos e smoke confirmados para cada redirect | Médio | unittest + build + smoke HTTP/browser |
| 5C | Remover páginas legacy não roteadas | Nenhuma importação runtime remanescente e testes atualizados | Médio | grep/import scan + unittest + build |
| 5D | Reduzir ou retirar `AppShell` legacy | 5B e 5C concluídas, navegação e busca global validadas | Médio/alto | smoke browser e visual QA |
| 5E | Isolar ou remover CSS legacy | AppShell e alias herdados já sem uso relevante | Alto | visual QA desktop/mobile + build |
| 5F | Auditoria visual final | CSS e shell estabilizados | Médio | browser QA autenticado |
| 5G | Checklist pré-push final | Fases 5B-5F concluídas | Baixo | gates completos + diff check |
