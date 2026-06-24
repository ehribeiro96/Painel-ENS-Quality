# Users Parity Matrix — 2026-06-23

Policy: POLICY_A_SAFE_REDIRECT

| Capacidade | /users legacy | Apoema Usuários | Paridade | Observação |
|---|---|---|---|---|
| Rota protegida | sim | sim | sim | ProtectedRoute preservado; alias temporário aponta para /apoema/users. |
| Lista/tabela de usuários | sim | sim | sim | A superfície nova preserva listagem, tabela e cartões de destaque. |
| Busca | sim | sim | sim | Busca textual continua ligada ao backend real. |
| Filtros | sim | sim | sim | Filtros operacionais e leitura por status continuam disponíveis. |
| Nome/e-mail | sim | sim | sim | Campos centrais permanecem explícitos. |
| Status ativo/inativo | sim | sim | sim | Situação operacional preservada com labels em PT-BR. |
| Papel/perfil | sim | sim | sim | Perfis continuam visíveis sem alterar RBAC. |
| Criar/editar/desativar | sim | sim | sim | Mantido sob canWrite/canDelete e contratos reais. |
| Detalhe por usuário | sim | sim | sim | Rota /apoema/users/:id expõe o mesmo cadastro com shell Apoema. |
| Vínculo com ativos | sim | sim | sim | Detalhe mantém a leitura de ativos vinculados. |
| Vínculo com assinatura | parcial | sim | ampliada | A superfície nova conecta o detalhe com /apoema/signatures. |
| Estado vazio | sim | sim | sim | Empty state explícito e controlado. |
| Loading/error | sim | sim | sim | Estados continuam explícitos. |
| PT-BR | sim | sim | sim | Textos operacionais em Português Brasileiro. |
| Responsividade | sim | sim | sim | A página passou para a superfície Apoema. |
| Integração com backend | sim | sim | sim | Continua usando os contratos reais de users e assets. |
