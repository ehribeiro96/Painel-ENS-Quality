# Signatures Parity Matrix — 2026-06-23

Policy: POLICY_A_SAFE_REDIRECT
Target: /apoema/signatures
Legacy alias: /signatures

| Capacidade | /signatures legacy | Apoema Assinaturas | Paridade | Observação |
|---|---|---|---|---|
| Rota protegida | Sim | Sim | Sim | Ambas ficam atrás de ProtectedRoute / ApoemaRoute. |
| Lista/tabela de assinaturas | Sim | Sim | Sim | A seleção por colaborador e o preview cobrem a navegação principal. |
| Busca | Não evidenciado | Não evidenciado | Parcial | O fluxo é focado em seleção direta, não em busca global. |
| Filtros | Não evidenciado | Não evidenciado | Parcial | Não havia filtro explícito na experiência anterior. |
| Status pendente/assinado | Sim | Sim | Sim | `Pendente`, `Gerada`, `Copiado` e `Pronto`. |
| Vínculo com ativo | Não evidenciado | Não evidenciado | Parcial | Assinaturas são vinculadas a colaborador, não a ativo. |
| Vínculo com responsável | Sim | Sim | Sim | O colaborador selecionado é o vínculo operacional. |
| Termo/documento | Sim | Sim | Sim | HTML da assinatura é gerado e baixado. |
| Histórico/detalhe | Parcial | Parcial | Parcial | O preview e o HTML cobrem a conferência principal. |
| Ações principais | Sim | Sim | Sim | Gerar, copiar e baixar permanecem disponíveis. |
| Estado vazio | Sim | Sim | Sim | `Base44EmptyState` preservado. |
| Loading/error | Sim | Sim | Sim | Estados explícitos preservados. |
| PT-BR | Sim | Sim | Sim | Textos em português. |
| Responsividade | Sim | Sim | Sim | Mantém o padrão visual Apoema. |
| Integração com backend | Sim | Sim | Sim | Usa API real de colaboradores e geração de assinatura. |
