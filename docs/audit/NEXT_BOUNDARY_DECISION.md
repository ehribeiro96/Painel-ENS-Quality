# Next Boundary Decision

Boundary atual concluída: `FRONTEND-AUTH-FREEZE-H1 — audit authenticated frontend freeze after login`.

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
- `AUTH-UAT-H1`: `PARTIAL_AUTH_SESSION_REQUIRED`; o caminho seguro foi definido via scripts documentados, mas a sessão autenticada não pôde ser obtida naquela execução.
- `FRONTEND-AUTH-FREEZE-H1`: `PARTIAL_AUTH_REQUIRED`; build e superfície pública foram validados, mas o freeze pós-login não foi reproduzido por ausência de sessão autenticada segura.

## Decisão objetiva

O frontend atual compila e o runtime público em `127.0.0.1:8000` responde corretamente. A superfície sem sessão mostrou `/login` estável e redirecionamento de `/` para `/login` sem loop visível. Não há evidência suficiente para corrigir auth/router/dashboard/assets nesta boundary.

O bloqueio principal continua sendo a ausência de uma sessão autenticada local segura que permita reproduzir o estado pós-login sem imprimir ou salvar senha, cookie, token, Authorization header ou storage state.

## Próxima boundary recomendada

1. `AUTH-UAT-H2 — provision documented local UAT test user`
   - Objetivo: viabilizar um usuário/sessão local repetível para auditoria visual autenticada.
   - Escopo: somente a trilha de autenticação local/UAT, sem alteração funcional ampla.
   - Critério de GO: sessão segura disponível para recheck, sem segredo em output, arquivo ou commit.

## Boundaries seguintes condicionais

2. `FRONTEND-AUTH-FREEZE-H1B — collect authenticated trace`
   - Condição: sessão UAT segura disponível.
   - Objetivo: reproduzir ou descartar o freeze após login com network/console/performance sanitizados.
   - Critério de GO: classificar uma das causas `FREEZE_*` ou `NOT_REPRODUCED` com evidência autenticada.

3. `FRONTEND-AUTH-FREEZE-H2 — fix authenticated freeze root cause`
   - Condição: H1B identificar causa raiz objetiva.
   - Objetivo: correção mínima do componente/rota/hook/API client afetado.
   - Critério de GO: teste/build e recheck autenticado provam ausência do freeze.

4. `HISTORY-H1 — improve asset history readability and audit traceability`
   - Condição: freeze não reproduzido ou resolvido, e prioridade voltar para legibilidade/rastreabilidade.
   - Deve preservar RBAC, paginação, imports, IA/Ollama, Docker, migrations e package-lock.

## O que não fazer agora

- Não implementar correção de frontend sem reprodução autenticada.
- Não alterar auth provider, router, API client, dashboard, assets ou CSS nesta boundary.
- Não criar bypass de login.
- Não hardcodar credencial.
- Não ler `.env*`, dumps, bancos, tokens ou credenciais.
- Não salvar storage state, cookies, tokens, Authorization header, screenshot sensível ou perfil de navegador.
- Não executar `git add .`, `git add -A`, reset, checkout, clean, push, merge ou rebase.
- Não alterar backend, migrations, Docker/Compose, package files, assets, CI ou IA/Ollama.

## Decisão final

Próxima boundary recomendada: `AUTH-UAT-H2 — provision documented local UAT test user`.

Justificativa executiva: o bug relatado é autenticado; sem auth path seguro, a auditoria só consegue provar que build, `/login` e redirecionamento público estão estáveis. A reprodução pós-login deve vir antes de qualquer correção funcional.
