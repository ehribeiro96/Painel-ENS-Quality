# Settings Parity Matrix — 2026-06-23

Policy: POLICY_A_SAFE_REDIRECT

| Capacidade | /settings legacy | Apoema Configurações | Paridade | Observação |
|---|---|---|---|---|
| Rota protegida | sim | sim | sim | ProtectedRoute preservado; alias temporário aponta para /apoema/settings. |
| Tema/aparência | sim | sim | sim | ThemeSelector e preferência visual seguem explícitos. |
| Preferências operacionais | sim | sim | sim | Lista de preferências permanece visível. |
| Segurança visual | sim | sim | sim | Nenhum token, senha ou header é renderizado. |
| RBAC/leitura | sim | sim | sim | Somente leitura; a superfície continua visual e sem expandir permissões. |
| Integrações/serviços | sim | sim | sim | A tela permanece descritiva, sem expor integração real sensível. |
| Estado vazio/loading/error | n/a | sim | ampliada | A superfície novo target mantém feedback visual estático. |
| PT-BR | sim | sim | sim | Textos operacionais em Português Brasileiro. |
| Responsividade | sim | sim | sim | Layout simples e compatível com a shell Apoema. |
| Integração com backend | não | não | sim | Não há chamada backend nessa superfície. |
