# Next Boundary Decision

## 1. Estado Pós-B3

- `GIT-C1 — Worktree boundary inventory and commit plan` foi concluído com `GO`; o plano de commits seletivos foi gerado sem stage nem commit.
- `GIT-C2 — selective commits by approved boundary plan` foi concluído com `PARTIAL`; os commits seletivos principais foram publicados e os ambíguos/ruídos de qualidade ficaram fora.
- `B0 — Segurança/higiene` foi concluído com `GO`.
- `B1 — Documentação de auditoria` foi consolidado.
- `B2 — AI Chat/backend hardening` foi fechado com `GO COM RESSALVAS`.
- `B3 — Import pipeline/staging` foi fechado com `GO`.
- `B4-A — Frontend shell/UX baseline` foi concluído com ressalva operacional.
- `B4-A2 — Frontend runtime normalization` foi concluído com recomendação de runtime único.
- `B4-A3 — Frontend WSL native runtime activation` foi concluído com `GO`.
- `B4-B — Frontend shell/UX smoke e ajustes mínimos` foi concluído com `GO COM RESSALVAS`.
- `B4-B2 — Frontend visual smoke validation` foi concluído com `GO COM RESSALVAS`.
- `B4-B3 — Frontend manual visual smoke closeout` foi superseded por `B4-C`.
- `B4-C — Frontend visual repair` foi concluido como `PARTIAL`: build passa, screenshots foram gerados e o reparo CSS estrutural foi aplicado, mas o shell autenticado ainda precisa de sessao real para smoke completo.
- `B4-D — Authenticated visual smoke and fine polish` foi concluido com `GO`: backend real, sessao real, screenshots autenticados e ajustes finos foram validados.
- `INFRA-D1 — Docker Engine nativo no WSL` foi concluido como `PARTIAL`: a auditoria confirmou que `docker`/Compose ainda vêm de symlinks do Docker Desktop em `/mnt/wsl/docker-desktop`, e a instalacao nativa ficou bloqueada porque `sudo -n` nao estava disponivel nesta sessao.
- `INFRA-D1B — Docker Engine nativo no WSL com sudo interativo` foi concluido como `PARTIAL`: `sudo -v` abriu prompt, mas a autenticacao nao ficou disponivel para a sessao de comandos; nenhuma alteracao de sistema foi aplicada.
- `INFRA-D1C — Docker Engine nativo no WSL via script root-assistido` foi concluido com `GO`: Docker CE oficial, Compose plugin nativo, `hello-world`, Postgres/Redis, backend e frontend foram validados no daemon WSL nativo.
- `B5-A — AI Chat Ollama local provider` foi concluido com `GO`: provider Ollama local integrado no backend FastAPI como proxy seguro; frontend segue chamando apenas `/api/v1/ai-chat`.
- `B5-B — AI Chat Ollama LAN OpenAI-compatible runtime smoke` foi concluido como `PARTIAL`: provider `ollama-lan` foi implementado com `/v1/chat/completions`, allowlist explicita, sem mock fallback, testes/backend/build passando; validacao real do host LAN e smoke UI autenticado ficaram pendentes.
- `B5-C — AI Chat Ollama LAN authenticated runtime validation` foi concluido como `PARTIAL`: TCP, `/v1/models`, `/v1/chat/completions` e provider backend real passaram; smoke UI autenticado ficou pendente porque a sessão do navegador não persistiu.
- `B5-D — AI Chat authenticated UI session fix/validation` foi concluída com `GO`; o smoke same-origin autenticado fechou a trilha com `qwen3:1.7b-64k` como baseline do `ollama-lan`.
- O candidato forte a segredo em `tools/composio_client.py` já foi removido do código e substituído por `COMPOSIO_API_KEY` no ambiente.
- A rotação externa da credencial continua necessária se a chave antiga era real.
- O worktree permanece misturado em várias áreas, então a próxima edição funcional precisa ser isolada por boundary.

## 2. Por que `B1` Vem Antes de Feature Funcional

`B1` consolida o mapa do projeto antes de qualquer feature nova:

- reduz duplicidade documental;
- define onde estão os relatórios oficiais;
- separa documentação de decisão de código funcional;
- evita que a próxima rodada misture suporte, segurança e feature numa mesma mudança.

## 3. O que Ainda Impede Edição Ampla

- O worktree continua com backend, frontend, testes e docs ao mesmo tempo.
- Há materiais experimentais e legados fora do fluxo principal.
- Existem boundaries futuras com blast radius diferente, e elas não devem ser misturadas.
- A validacao visual autenticada do shell React foi concluida em `B4-D`.
- O risco visual remanescente esta concentrado nas rotas legadas `/assinaturas/` e `/admin/`, fora do shell React.
- O runtime Docker local foi comprovado como nativo WSL em `INFRA-D1C`.
- Volumes do Docker Desktop nao foram migrados; se dados antigos forem necessarios, abrir boundary separada.

## 4. Recomendação Objetiva

1. Consolidar documentação em `B1`.
2. Executar `GIT-C2 — executar commits seletivos aprovados` antes de abrir nova feature.
3. Não misturar imports, frontend, migrations e IA no mesmo ciclo.

### Recomendação padrão

`GIT-C3 — revisar ambíguos remanescentes` é a próxima ação mais segura.

Se a prioridade voltar para feature antes de triagem adicional, a alternativa documentada segue sendo `B4-E — legacy CSP and route polish`.

## 5. Critério para Escolher `B4`

Escolha `B4-E` quando o foco for:

- CSP/fontes das rotas legadas;
- visual de `/assinaturas/` e `/admin/`;
- validacao separada de legado, sem misturar com o shell React;
- decisao explicita sobre manter fontes externas ou servir assets locais.

## 7. O que Não Fazer Agora

- Nao iniciar outro reparo CSS amplo sem evidencia visual autenticada.
- Não mexer em migrations.
- Não promover Ollama como default.
- Não commitar arquivos sensíveis.
- Não misturar boundaries num único PR.
- Não usar documentação como substituto de validação funcional.
- Não rodar `docker compose down -v`, prune ou remoção de volumes para resolver a migração Docker.

## 8. Decisão Final

**Boundary funcional recomendada: `GIT-C2 — executar commits seletivos aprovados`.**

Motivo: o worktree está inventariado, o stage está vazio e o plano de commits seletivos foi produzido sem alterar código funcional. Depois de GIT-C2, a prioridade pode voltar para `B4-E` ou outra boundary funcional já fechada conforme necessidade de negócio.
