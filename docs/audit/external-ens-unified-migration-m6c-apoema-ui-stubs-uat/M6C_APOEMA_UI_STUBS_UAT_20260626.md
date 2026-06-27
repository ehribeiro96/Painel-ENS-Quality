# M6C Apoema UI Stubs UAT

## 1. Status
PARTIAL-GO

## 2. Objetivo
Validar visual e funcionalmente os stubs Artifacts, RAG e Designer no Apoema.

## 3. Base M6B
- M6B preservado: sim.
- Rotas criadas em M6B: `/apoema/artifacts`, `/apoema/rag`, `/apoema/designer`, `/apoema-preview/artifacts`, `/apoema-preview/rag`, `/apoema-preview/designer`.
- Aliases legacy: não criados.
- Providers reais, MCP real, vector store real e geração real de imagem: desativados.
- Playwright autenticado no M6B: sim.

## 4. Ambiente
- Vite: `http://127.0.0.1:5175`.
- Session file: presente fora do repositório, mas inválido para este ciclo.
- Playwright: disponível.
- Viewports: 1366x768, 1440x900, 1920x1080, 390x844, 768x1024.
- Rotas auditadas: /apoema, /apoema/artifacts, /apoema/rag, /apoema/designer, /apoema/chat, /apoema/settings, /apoema-preview/artifacts, /apoema-preview/rag, /apoema-preview/designer.

## 5. Rotas auditadas
Referência: `maps/uat-route-matrix.tsv`.

## 6. Resultado visual
- Todas as 45 combinações rota/viewport terminaram na tela de login.
- Nenhuma tela dos stubs M6B foi alcançada de forma autenticada.
- Não houve tela branca ou crash; houve bloqueio de sessão.
- Screenshots foram capturados, mas mostram apenas a tela de login.

## 7. Resultado funcional Artifacts
- Não validado nesta execução porque `/apoema/artifacts` redirecionou para login.
- Upload, listagem, download temporário e exclusão não foram exercitados.

## 8. Resultado funcional RAG
- Não validado nesta execução porque `/apoema/rag` redirecionou para login.
- Busca, collections e auditoria recente não foram exercitadas.

## 9. Resultado funcional Designer
- Não validado nesta execução porque `/apoema/designer` redirecionou para login.
- Criação de job, ajuste, refresh e cancelamento não foram exercitados.

## 10. Teclado/foco
- Teste de Tab foi executado no viewport desktop.
- O fluxo alcançou apenas a tela de login; o conteúdo autenticado não ficou disponível.
- Referência: `maps/keyboard-focus-matrix.tsv`.

## 11. Segurança e rede
- Nenhum domínio de provider real apareceu.
- Nenhuma chave real foi observada.
- A rede mostrou apenas `auth/refresh` com respostas `401` e `429` enquanto a sessão falhava.
- Nenhum material sensível foi persistido no relatório.

## 12. Correções aplicadas
- Nenhuma.
- A falha é de sessão/UAT, não de UI do Apoema.

## 13. Validações
- `git diff --check`: PASS.
- `ruff check backend tests scripts`: PASS.
- `compileall`: PASS.
- `npm run build`: PASS.
- `unittest discover`: PASS com 325 testes e 8 skips.
- `pytest`: não forneceu sinal confiável neste runtime por falha de captura do runner.

## 14. Riscos restantes
- Sessão UAT expirada ou ausente para o fluxo autenticado.
- As telas M6B ainda não foram avaliadas em uso real com sessão válida.
- Repetidas tentativas de refresh bateram em rate limiting.

## 15. Próxima fase recomendada
Renovar a sessão UAT segura fora do repositório e repetir o UAT autenticado M6C.
