# PRODUCT-H1 — Cenários UAT

Objetivo: validar o MVP operacional com dados sintéticos e evidência segura. Não usar dados produtivos, `.env`, dumps, tokens, credenciais ou planilhas reais de usuários.

## Regras de execução

- Começar com stage vazio.
- Registrar ambiente, usuário/perfil, data/hora e build/commit local.
- Usar massa sintética: nomes fictícios, emails de exemplo e patrimônio não real.
- Não executar apply de importação em base produtiva.
- Não alterar código durante UAT; bugs viram boundaries específicas.
- Evidências podem ser screenshot, IDs sintéticos, resposta HTTP redigida ou linha de auditoria sem segredo.

## Cenário 1 — Registrar ativo

Pré-condição:
- Usuário autenticado com perfil ADMIN ou TECHNICIAN.
- Ambiente local apontando para banco de teste/desenvolvimento.

Passos:
1. Acessar tela de ativos.
2. Criar ativo sintético com pelo menos hostname, patrimônio ou serial.
3. Informar tipo, status, localidade e usuário quando aplicável.
4. Salvar.
5. Abrir detalhe do ativo.

Resultado esperado:
- Ativo aparece na lista e no detalhe.
- Backend aceita somente identidade mínima válida.
- Auditoria registra criação do ativo.

Evidência:
- Screenshot/lista com ativo sintético.
- ID do ativo sintético.
- Linha de auditoria `CREATE Asset`.

Critério de GO/NO-GO:
- GO se ativo persistir, for consultável e auditado.
- NO-GO se ativo sem identidade for aceito ou se criação não for auditada.

## Cenário 2 — Importar ativo

Pré-condição:
- Usuário ADMIN ou TECHNICIAN.
- Planilha CSV/XLSX sintética sem fórmulas perigosas.
- Import mode adequado (`INITIAL_LOAD`, `SAFE_REIMPORT` ou `PREVIEW_ONLY`) definido conscientemente.

Passos:
1. Acessar Importação Lansweeper.
2. Fazer upload da planilha sintética.
3. Revisar preview, mapping, staging, conflitos e validation errors.
4. Se não houver blockers, aplicar importação em base local/dev.
5. Localizar ativo importado na tela de ativos.

Resultado esperado:
- Upload cria `ImportJob` em staging.
- Preview e staging mostram dados normalizados.
- Conflitos bloqueiam apply quando existirem.
- Ativo importado aparece na lista após apply seguro.
- Auditoria registra upload/apply.

Evidência:
- ID do `ImportJob`.
- Contadores de linhas válidas/inválidas/conflitos.
- ID do ativo sintético importado.
- Linha de auditoria `IMPORT ImportJob`.

Critério de GO/NO-GO:
- GO se staging/review/apply seguro funcionarem e o ativo final for consultável.
- NO-GO se apply ocorrer com conflito bloqueante ou sem confirmação.

## Cenário 3 — Criar movimentação

Pré-condição:
- Ativo sintético existente.
- Usuário destino sintético existente quando status final for `IN_USE`.

Passos:
1. Abrir detalhe do ativo.
2. Clicar em Movimentar.
3. Alterar usuário/status/localidade.
4. Preencher justificativa.
5. Marcar confirmação explícita.
6. Confirmar movimentação.

Resultado esperado:
- Backend salva `AssetMovement`.
- Estado atual do ativo muda.
- Histórico atualiza.
- Auditoria registra `MOVE Asset`.

Evidência:
- ID do movimento.
- Antes/depois no histórico.
- Linha de auditoria `MOVE Asset`.

Critério de GO/NO-GO:
- GO se movimento for persistido uma vez, com histórico e auditoria.
- NO-GO se status `IN_USE` aceitar usuário vazio ou se movimento não aparecer no histórico.

## Cenário 4 — Gerar macro

Pré-condição:
- Cenário 3 concluído com movimento salvo.
- Template `ativos-atualizar-inventario` disponível e ativo.

Passos:
1. Após movimentar, solicitar/observar macro sugerida da movimentação.
2. Conferir texto gerado.
3. Conferir campos pendentes, se existirem.
4. Confirmar que existe `generation_id`.

Resultado esperado:
- Macro é gerada somente após `movement_id` existir.
- `MacroGeneration` é vinculada a `context_type=asset_movement` e `context_id=<movement_id>`.
- Pendências são visíveis.

Evidência:
- ID da macro gerada.
- ID do movimento vinculado.
- Texto renderizado sintético.
- Auditoria `asset_movement_macro_generated` / `macro_generated`.

Critério de GO/NO-GO:
- GO se macro persistida e vinculada aparecer para o operador.
- NO-GO se macro for apenas texto local sem persistência ou se ficar invisível ao usuário por fechamento de modal.

## Cenário 5 — Copiar macro

Pré-condição:
- Macro do Cenário 4 possui `generation_id`.
- Clipboard disponível no navegador.

Passos:
1. Clicar em Copiar macro.
2. Colar em campo neutro/local para conferir texto sintético.
3. Consultar auditoria ou geração para confirmar `copied=true`.

Resultado esperado:
- Texto vai para clipboard.
- Backend marca macro como copiada.
- Auditoria registra `macro_copied`.

Evidência:
- Mensagem de sucesso.
- `generation_id` com `copied=true` ou evento de auditoria.

Critério de GO/NO-GO:
- GO se copiar e marcar copied forem consistentes.
- NO-GO se o botão copiar estiver ativo sem `generation_id` ou se auditoria não registrar a cópia.

## Cenário 6 — Ver histórico

Pré-condição:
- Ativo com pelo menos uma movimentação sintética.

Passos:
1. Abrir detalhe do ativo.
2. Ir até Timeline de movimentações.
3. Conferir data/hora, antes, depois e justificativa.

Resultado esperado:
- Histórico vem de dado real persistido.
- Movimentações aparecem em ordem decrescente.
- Justificativa e alteração de status/local/usuário são legíveis.

Evidência:
- Screenshot da timeline.
- ID do ativo e ID do movimento.

Critério de GO/NO-GO:
- GO se timeline permitir entender a mudança sem consultar banco.
- NO-GO se só exibir IDs inutilizáveis ou omitir justificativa.

## Cenário 7 — Ver auditoria

Pré-condição:
- Cenários 1 a 5 executados.
- Usuário ADMIN ou MANAGER.

Passos:
1. Acessar Auditoria.
2. Localizar eventos recentes.
3. Conferir ação, entidade, ator, fonte, data/hora e rastreamento.

Resultado esperado:
- Eventos aparecem com paginação atual.
- Ações críticas estão presentes: create asset, move asset, macro generated, macro copied, import quando aplicável.
- Usuário sem permissão não acessa a tela.

Evidência:
- Screenshot de auditoria com dados sintéticos.
- Lista de eventos esperados encontrados.

Critério de GO/NO-GO:
- GO se eventos críticos forem rastreáveis.
- NO-GO se auditoria não exibir eventos ou se perfis indevidos acessarem.

## Cenário 8 — Usar AI Chat para apoiar, sem alterar dado

Pré-condição:
- AI Chat habilitado no ambiente local.
- Provider `ollama-lan` disponível ou indisponibilidade registrada como limitação.

Passos:
1. Acessar AI Chat.
2. Perguntar explicação de uma macro sintética.
3. Pedir sugestão de melhoria textual sem mandar salvar.
4. Confirmar que nenhum ativo/movimento/template/import foi alterado.

Resultado esperado:
- IA responde como assistente textual.
- Saída não inclui `<think>`.
- Nenhum dado operacional muda sem ação humana explícita.

Evidência:
- Screenshot da resposta redigida.
- Confirmação de ausência de alterações em histórico/auditoria operacional além de logs próprios do chat, se houver.

Critério de GO/NO-GO:
- GO se IA apoiar sem executar ação.
- NO-GO se IA alterar dados ou se browser chamar provider LAN diretamente.

## Cenário 9 — Validar erro de importação

Pré-condição:
- Planilha sintética inválida, com duplicidade, coluna faltante ou fórmula perigosa.

Passos:
1. Fazer upload do arquivo inválido.
2. Conferir validation errors/conflitos.
3. Tentar apply quando houver blocker.
4. Confirmar bloqueio seguro.

Resultado esperado:
- Erros aparecem na UI.
- Apply é bloqueado quando há conflito/invalidade relevante.
- Auditoria registra tentativa/upload sem aplicar dado inseguro.

Evidência:
- ID do job.
- Mensagem de blocker.
- Contadores invalid/conflict.

Critério de GO/NO-GO:
- GO se erro for claro e apply não acontecer.
- NO-GO se dado inválido for aplicado ou se erro for silencioso.

## Cenário 10 — Validar permissão/segurança

Pré-condição:
- Usuários sintéticos com perfis ADMIN, TECHNICIAN, MANAGER e perfil comum se existir.

Passos:
1. Validar acesso a imports/macros para ADMIN/TECHNICIAN.
2. Validar audit logs para ADMIN/MANAGER.
3. Validar settings somente ADMIN.
4. Tentar acessar rota sem token ou com sessão expirada.

Resultado esperado:
- RBAC bloqueia perfis indevidos.
- 401/403 são tratados pela UI/API.
- Não há exposição de dados sensíveis no frontend.

Evidência:
- Matriz perfil x rota.
- Status HTTP ou screenshot de bloqueio.

Critério de GO/NO-GO:
- GO se restrições forem coerentes com `App.tsx` e backend dependencies.
- NO-GO se perfil indevido executar ação crítica.
