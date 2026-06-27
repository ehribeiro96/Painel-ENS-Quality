# M6C Apoema UI Stubs UAT

## 1. Status
PARTIAL-GO: UAT visual/autenticado passou sem redirects, sem P0/P1 visual, sem provider real e com gates técnicos verdes. Reserva: a busca RAG com a query exigida `seguros` mostrou empty state controlado, pois o mock backend atual não possui documento/keyword correspondente; como backend está fora da boundary M6C, isso foi registrado como limitação funcional do mock para a próxima fase.

## 2. Objetivo
Validar visual e funcionalmente os stubs Artifacts/RAG/Designer no Apoema, sem criar feature nova e sem alterar backend, Docker ou migrations.

## 3. Base M6B
M6B preservado como GO nos commits `17f31bd` e `28769d8`. Rotas M6B continuaram presentes, aliases legacy não foram reintroduzidos, clients continuam backend-only via `/api/v1`, e storageState permaneceu fora do repositório.

## 4. Ambiente
- Projeto: `/home/estevaoqualityadm/projects/Painel-ENS-Quality`.
- Branch: `main`.
- Runtime backend: `http://localhost:8080`, `/health/ready` retornou `200 OK`.
- Vite Apoema: `http://127.0.0.1:5175` já estava ativo na porta 5175.
- Auth UAT: storageState em `/tmp/apoema-uat-auth-state.json`; credencial local temporária em `/tmp/apoema-m6c-uat-credentials.txt`, modo `0600`, sem versionamento e sem impressão de senha.
- Usuário UAT local: criado no banco local via container `app` para recompor storageState; não houve alteração de código backend.

## 5. Rotas auditadas
Foram auditadas 9 rotas em 5 viewports, totalizando 45 capturas:

- `/apoema`
- `/apoema/artifacts`
- `/apoema/rag`
- `/apoema/designer`
- `/apoema/chat`
- `/apoema/settings`
- `/apoema-preview/artifacts`
- `/apoema-preview/rag`
- `/apoema-preview/designer`

Viewports: `390x844`, `768x1024`, `1366x768`, `1440x900`, `1920x1080`.

Evidência: `maps/uat-route-matrix.tsv` e `screenshots/*.png`.

## 6. Resultado visual
Visual status: GO_WITH_RESERVATION.

- 45/45 rotas/viewports renderizaram sem `/login`.
- 45 screenshots criados.
- Sem tela branca.
- Sem overflow horizontal crítico detectado.
- Labels principais em PT-BR visíveis.
- Badges/copy de `Backend`, `Mock`, `Mock determinístico`, `backend-owned` ou `sem provider real` visíveis conforme tela.
- Os console/request failures registrados no raw foram do cenário sintético de backend unavailable para RAG e não representam falha da navegação normal.

Evidência: `maps/visual-findings.tsv`.

## 7. Resultado funcional Artifacts
Artifacts UAT: OK.

- Lista carregou com estado legível.
- Upload de arquivo pequeno `/tmp/apoema-m6c/artifact-uat.txt` foi aceito.
- UI manteve copy de storage backend-owned.
- Metadata não exibiu path interno.
- Obtenção de link assinado funcionou sem logar URL sensível completa.
- Excluir foi exercido; o arquivo temporário `artifact-uat.txt` não permaneceu listado na inspeção posterior.
- Estados loading/empty/error/unauthorized/backend unavailable estão implementados na UI.

Observação: a matriz raw marcou `delete=fail` por critério textual estrito do runner, mas a inspeção posterior confirmou que o arquivo temporário não permaneceu visível.

## 8. Resultado funcional RAG
RAG UAT: parcial.

- Collections carregaram.
- Contexto de curso carregou.
- Auditoria recente carregou/mostrou estado controlado conforme permissão.
- A tela deixa claro que MCP real, vector store e provider real não estão ativos.
- A busca com query exigida `seguros` executou via `/api/v1/rag/search`, mas retornou empty state controlado porque o mock backend atual não contém termo/documento `seguros`.
- Não foi feita correção backend nesta fase por boundary explícita.

## 9. Resultado funcional Designer
Designer UAT: OK.

- Health, templates e form-options carregaram.
- Criação de job mock com prompt controlado funcionou.
- Job id/status/items apareceram.
- Ações adjust/refresh/cancel foram acionadas contra `/api/v1/designer/*`.
- A UI deixa claro que não há geração real de imagem nem provider real.
- `download-url bloqueado/não disponível` permanece explícito.

## 10. Teclado/foco
Teclado/foco: OK.

- Validação desktop `1366x768` em `/apoema/artifacts`, `/apoema/rag`, `/apoema/designer`.
- Tab percorreu navegação e controles principais.
- Foco visual detectado.
- Enter/Space destrutivo não foi pressionado em excluir/cancelar para não alterar estado além do UAT controlado.

Evidência: `maps/keyboard-focus-matrix.tsv`.

## 11. Segurança/provider scan
- Chamadas observadas somente para `/api/v1/artifacts`, `/api/v1/rag`, `/api/v1/designer`, `/api/v1/ai-chat` e `/api/v1/auth/refresh`.
- Nenhuma chamada direta para OpenAI/Gemini/Google APIs/Vertex/Imagen/Ollama/Composio provider externo.
- Nenhuma signed URL completa foi gravada em docs/raw.
- Nenhum Authorization/Cookie/Set-Cookie foi persistido no relatório.
- Grep de secrets retornou falsos positivos esperados: nomes de testes, strings `Bearer` em clients, e provider ids mock/ollama/hermes já existentes do chat. Nenhum segredo real encontrado.

## 12. Correções aplicadas
Nenhuma correção de código foi aplicada. Nenhum arquivo frontend/backend/test foi alterado nesta fase. Apenas artefatos de auditoria M6C foram criados.

## 13. Validações
Executadas e salvas em `m6c-apoema-ui-stubs-uat-gates.log`:

- `git diff --check`: OK.
- `PYTHONPATH=backend .venv/bin/python -m pytest`: `336 passed, 22 skipped`.
- `.venv/bin/python -m ruff check backend tests scripts`: OK.
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: OK.
- `npm run build`: OK.
- Secret/provider scan: sem segredo real; falsos positivos documentados.

## 14. Riscos restantes
- Query RAG `seguros` não retorna citação mock porque o backend mock atual não contém esse termo. Próxima boundary deve decidir entre ajustar massa mock backend ou mudar a query UAT para termo existente.
- Auth refresh tem rotação; smokes futuros devem regenerar storageState imediatamente antes da matriz ou navegar dentro da SPA para evitar redirects artificiais.
- Usuário UAT local foi criado/atualizado apenas no banco local para viabilizar UAT; credencial temporária permanece fora do repo em `/tmp`.

## 15. Próxima fase recomendada
M7_PRE_PUSH_FINAL_READINESS, com atenção ao backlog RAG mock/query `seguros` antes de promover GO pleno de UAT funcional RAG.
