# Next Boundary Decision

Boundary atual concluída: `AUTH-UAT-H1 — define safe local UAT authentication path`.

## Estado consolidado

- `AUDIT-H1`: `PARTIAL` por untracked antigos, mas relatórios H1 seguem como base ativa de auditoria.
- `GIT-H2`: `PARTIAL` por grande volume de untracked, com triagem e matriz de decisão preservadas.
- `SEC-H2`: `GO COM RESSALVAS`; artefatos locais sensíveis seguem sem abertura de conteúdo e exigem revisão humana/manual.
- `DOCS-H2`: `GO`; consolidou documentos ativos e históricos.
- `IGNORE-H2`: `GO`; protege artefatos locais/sensíveis já classificados.
- `CI-H3`: `PARTIAL` aceitável por ausência de `actionlint`; workflow Docker foi endurecido como manual build-only.
- `LEGACY-H2`: `GO` documental; assets remanescentes foram inventariados por metadados sem abertura de binários/imagens.
- `TEST-H2`: `PARTIAL`; markers pytest e comandos de validação foram padronizados com ressalva conhecida de marker `ai_chat` sem testes marcados na boundary.
- `PRODUCT-H1`: `GO documental`; roadmap, MVP, backlog, UAT scenarios, do-not-touch e sumário executivo foram criados sem alteração funcional.
- `UAT-H1`: `GO COM RESSALVAS`; cenário ponta-a-ponta validado com dados sintéticos, com ressalva de UX porque a modal de movimentação fecha antes de manter a macro visível para cópia.
- `MACRO-H1`: `PARTIAL_RUNTIME_BLOCKED`; a correção de frontend foi aplicada no código-fonte, mas a revalidação do bundle atualizado ficou bloqueada pelo ambiente WSL/UNC e pela dependência opcional ausente do Rollup.
- `MACRO-H1B`: `PARTIAL_RUNTIME_RECHECK_BLOCKED`; o bundle novo foi servido com sucesso após `npm ci` e build em Node Linux, mas o recheck autenticado não pôde ser repetido porque a sessão local/admin não estava disponível nesta boundary.
- `MACRO-H1C`: `PARTIAL_AUTH_SESSION_REQUIRED`; a rechecagem visual autenticada não pôde ser completada de forma segura sem uma sessão local válida do app nesta boundary.
- `AUTH-UAT-H1`: `PARTIAL_AUTH_SESSION_REQUIRED`; o caminho seguro foi definido via scripts documentados, mas a sessão autenticada não pôde ser obtida nesta execução.

## Decisão objetiva

O fluxo alvo segue corrigido no frontend e o build foi revalidado em ambiente Linux. O último bloqueio é a disponibilidade de uma sessão autenticada local segura para completar a rechecagem visual.

- `/assets/{asset_id}/move` salva movimentação.
- `/assets/{asset_id}/history` lista histórico.
- `/movements/{movement_id}/suggested-macro` gera macro pós-movimentação.
- `/macros/generations/{generation_id}/copied` marca cópia.
- `/audit-logs` permite consulta de auditoria.

O código-fonte já contém a correção conservadora, mas a revalidação visual depende de um runtime frontend funcional que o ambiente local não conseguiu fornecer.

## Próxima boundary recomendada

1. `AUTH-UAT-H2 — provision documented local UAT test user`
   - Objetivo: viabilizar um usuário/sessão local repetível sem expor segredos.
   - Escopo: somente a trilha de autenticação local para UAT visual.
   - Critério de GO: sessão segura disponível para recheck.

## Boundaries seguintes condicionais

2. `MACRO-H1C — runtime visual recheck only`
   - Condição: a sessão autenticada local segura estiver disponível.
   - Objetivo: repetir a validação visual autenticada do fluxo de macro pós-movimentação agora que o build foi revalidado.
   - Escopo: recheck visual/UAT sem alterar código funcional.
   - Critério de GO: fluxo visual confirma a macro visível/copiável.

3. `MOV-H1 — movement creation and validation hardening`
   - Condição: UAT-H1 identificar lacuna em criação/validação/legibilidade de movimentação.
   - Não deve mexer em imports, IA/Ollama, legacy, Docker ou migrations.

4. `MACRO-H1 — ITIL macro generation polish`
   - Condição: o fluxo já revalidado mostrar oportunidade adicional de refinamento da macro oficial.
   - Não deve trocar template oficial sem revisão humana.

5. `HISTORY-H1 — history and audit traceability`
   - Condição: UAT-H1 mostrar dificuldade de rastrear movimento/macro/auditoria.
   - Deve preservar RBAC e paginação.

6. `RELEASE-H1 — production readiness checklist`
   - Condição: UAT-H1 e correções P1 concluídas ou riscos aceitos.
   - Não deve publicar imagem, push ou rodar migrations em banco produtivo.

## O que não fazer agora

- Não implementar feature antes do UAT-H1.
- Não fazer `git add .`, `git add -A` ou stage amplo.
- Não commitar/pushar nesta boundary.
- Não limpar untracked antigos.
- Não mexer em `.env*`, dumps, bancos, tokens ou credenciais.
- Não alterar backend, frontend, migrations, Docker, package-lock, assets, CI ou IA/Ollama dentro de UAT-H1.
- Não usar dado produtivo nos cenários.
- Não abrir DOCX/imagens/legacy assets sem boundary e decisão humana.

## Decisão final

Próxima boundary recomendada: `AUTH-UAT-H2 — provision documented local UAT test user`.

Justificativa executiva: o ajuste está codificado, mas a garantia operacional depende de um runtime frontend funcional para provar o comportamento na UI atualizada. O próximo passo deve restaurar essa capacidade de validação antes de avançar para HISTÓRIA ou outras evoluções.
