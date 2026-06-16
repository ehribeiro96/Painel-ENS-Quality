# Audit Index

## 1. Visão Geral

Este diretório concentra a leitura operacional da auditoria e dos relatórios de higiene do projeto.

Estado atual:

- `GIT-C1 — Worktree boundary inventory and commit plan`: concluído com `GO`; stage vazio e plano de commits seletivos gerado.
- `GIT-C2 — selective commits by approved boundary plan`: concluído com `PARTIAL`; commits seletivos principais foram criados e os ambíguos/ruídos de qualidade ficaram para `GIT-C3`.
- `GIT-C3 — revisar ambíguos remanescentes`: concluído com `PARTIAL`; arquivos seguros foram commitados e os remanescentes de qualidade ficaram documentados.
- `B0 — Segurança/higiene`: concluído com `GO`.
- `B1 — Documentação de auditoria`: em consolidação.
- `B2`: concluído com ressalva operacional.
- `B3`: concluído com validação dedicada.
- `B4-A — Frontend shell/UX baseline`: concluído com ressalva operacional; TypeScript passa, mas a estabilização do build ainda depende do runtime do ambiente.
- `B4-A2 — Frontend runtime normalization`: concluído com recomendação explícita de WSL nativo; build ainda não é reprodutível no runtime misto.
- `B4-A3 — Frontend WSL native runtime activation`: concluído com `GO`; build reprodutível no runtime WSL.
- `B4-B — Frontend shell/UX smoke e ajustes mínimos`: concluído com `GO COM RESSALVAS`; ajustes mínimos aplicados em `styles.css`.
- `B4-B2 — Frontend visual smoke validation`: concluído com `GO COM RESSALVAS`; build e preview passaram, smoke visual automatizado não foi possível nesta sessão.
- `B4-B3 — Frontend manual visual smoke closeout`: superseded por `B4-C`; a validacao manual foi substituida por smoke automatizado parcial com Playwright temporario.
- `B4-C — Frontend visual repair`: concluido como `PARTIAL`; build passa e screenshots foram gerados, mas smoke visual autenticado ainda depende de sessao valida.
- `B4-D — Authenticated visual smoke and fine polish`: concluido com `GO`; backend real, sessao real e screenshots autenticados foram validados, com ajustes finos pequenos.
- `B4-E — Legacy CSP and route polish`: concluido com `GO`; Google Fonts foram removidas do legado e o stack passou a usar fontes locais/sistemicas.
- `B5-A — AI Chat Ollama local provider`: concluido com `GO`; backend FastAPI agora suporta provider Ollama local como proxy seguro, sem expor Ollama ao frontend.
- `B5-B — AI Chat Ollama LAN OpenAI-compatible runtime smoke`: concluido como `PARTIAL`; provider `ollama-lan` foi implementado com allowlist e testes/build passaram, mas a validacao real do host LAN e o smoke UI autenticado ficaram pendentes.
- `B5-C — AI Chat Ollama LAN authenticated runtime validation`: concluido como `PARTIAL`; TCP, `/v1/models`, `/v1/chat/completions` e provider backend real passaram; smoke UI autenticado ficou pendente por sessão não persistida no browser.
- `B5-D — AI Chat authenticated UI session fix/validation`: concluído com `GO`; o smoke autenticado same-origin fechou a sessão UI com `qwen3:1.7b-64k` como baseline do `ollama-lan`.
- `INFRA-D1 — Docker Engine nativo no WSL`: concluido como `PARTIAL`; diagnostico confirmou dependencia de Docker Desktop e a instalacao nativa ficou bloqueada por ausencia de `sudo -n` nesta sessao.
- `INFRA-D1B — Docker Engine nativo no WSL com sudo interativo`: concluido como `PARTIAL`; o prompt `sudo -v` abriu, mas a autenticacao nao chegou ao processo desta sessao, entao nenhuma alteracao de sistema foi feita.
- `INFRA-D1C — Docker Engine nativo no WSL via script root-assistido`: concluido com `GO`; Docker CE oficial, Compose plugin nativo, Postgres/Redis, backend e frontend foram validados no daemon WSL nativo.
- `B5` e `B6`: continuam como boundaries posteriores e isoladas.
- O worktree ainda está misturado com mudanças de múltiplas áreas; isso não é um bloqueio para docs, mas continua sendo um bloqueio para edição funcional ampla.

## 2. Estado Atual do Projeto

- Há relatórios de auditoria, triagem e higiene espalhados na raiz de `docs/` e em `docs/audit/`.
- `docs/audit/` deve ser tratado como índice canônico para leitura humana da auditoria.
- Os relatórios da raiz continuam úteis como sumários e decisões operacionais.

## 3. Ordem Segura de Edição

1. Consolidar documentação e referências cruzadas em `B1`.
2. Escolher uma única boundary funcional entre `B3` e `B4`.
3. Seguir para `B6` ou abrir uma nova boundary funcional apenas após revisar os remanescentes que ficaram documentados em `GIT-C3`.
4. Só depois avançar para `B5` se houver necessidade de documentação/IA.
5. Usar `B6` apenas para testes e infra quando estiver isolado.

## 4. Status por Boundary

| Boundary | Status | Leitura principal | Observação |
|---|---|---|---|
| `B0` Segurança/higiene | Concluído | [SECURITY_HYGIENE_B0_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/SECURITY_HYGIENE_B0_REPORT.md) | Segredo hardcoded tratado; rotação externa segue necessária se a credencial era real. |
| `B1` Documentação de auditoria | Em andamento | [GENERAL_PROJECT_AUDIT_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/GENERAL_PROJECT_AUDIT_REPORT.md) | Este índice é a referência operacional da boundary. |
| `B2` AI Chat/backend hardening | Concluído com ressalva operacional | [AI_CHAT_BACKEND_HARDENING_B2_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_BACKEND_HARDENING_B2_REPORT.md) | Menor superfície que imports/frontend amplo; frontend build final falhou por ambiente WSL/UNC/`tsc`. |
| `B3` Import pipeline/staging | Concluído | [IMPORT_PIPELINE_STAGING_B3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_PIPELINE_STAGING_B3_REPORT.md) | Pipeline validado; manter boundaries futuras isoladas. |
| `B4-A` Frontend shell/UX baseline | Concluído com ressalva operacional | [FRONTEND_SHELL_UX_B4A_BASELINE_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_SHELL_UX_B4A_BASELINE_REPORT.md) | `tsc -b` passa; `npm run build` continua preso ao wrapper WSL/UNC e `vite build` ao runtime/dependência opcional. |
| `B4-A2` Frontend runtime normalization | Concluído com ressalva operacional | [FRONTEND_RUNTIME_NORMALIZATION_B4A2.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_RUNTIME_NORMALIZATION_B4A2.md) | Recomenda WSL nativo como runtime único; não executar `npm ci` ou `rm -rf node_modules` nesta boundary. |
| `B4-A3` Frontend WSL native runtime activation | Concluído com `GO` | [FRONTEND_WSL_NATIVE_RUNTIME_B4A3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_WSL_NATIVE_RUNTIME_B4A3_REPORT.md) | Node/NPM Linux ativos via `nvm`; `npm ci`, `tsc -b`, `vite build` e `npm run build` passam. |
| `B4-B` Frontend shell/UX smoke e ajustes mínimos | Concluído com ressalvas | [FRONTEND_SHELL_UX_B4B_SMOKE_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_SHELL_UX_B4B_SMOKE_REPORT.md) | Ajustes mínimos aplicados em `styles.css`; build passou. |
| `B4-B2` Frontend visual smoke validation | Concluído com ressalvas | [FRONTEND_VISUAL_SMOKE_B4B2_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_VISUAL_SMOKE_B4B2_REPORT.md) | Preview e roteamento estático passaram; smoke visual automatizado não foi possível nesta sessão. |
| `B4-B3` Frontend manual visual smoke closeout | Superseded | [FRONTEND_MANUAL_VISUAL_SMOKE_B4B3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_MANUAL_VISUAL_SMOKE_B4B3_REPORT.md) | Substituido pela boundary `B4-C`, que instalou Playwright temporariamente fora do repo e gerou screenshots parciais. |
| `B4-C` Frontend visual repair | Concluido como `PARTIAL` | [FRONTEND_VISUAL_REPAIR_B4C_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_VISUAL_REPAIR_B4C_REPORT.md) | CSS estrutural reparado; build passa; shell autenticado ainda precisa de smoke com sessao real. |
| `B4-D` Authenticated visual smoke and fine polish | Concluido com `GO` | [FRONTEND_AUTHENTICATED_VISUAL_SMOKE_B4D_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/FRONTEND_AUTHENTICATED_VISUAL_SMOKE_B4D_REPORT.md) | Backend real e sessao real validados; screenshots autenticados gerados; ajustes finos em DataTable e AI Chat. |
| `B4-E` Legacy CSP and route polish | Concluido com `GO` | [LEGACY_CSP_ROUTE_POLISH_B4E_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/LEGACY_CSP_ROUTE_POLISH_B4E_REPORT.md) | Legado `/admin/` e `/assinaturas/` preservado; fontes externas removidas e stack local/sistemica aplicado. |
| `B5-A` AI Chat Ollama local provider | Concluido com `GO` | [AI_CHAT_OLLAMA_B5A_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_B5A_REPORT.md) | Provider Ollama local integrado no backend como proxy seguro; frontend segue chamando somente backend. |
| `B5-B` AI Chat Ollama LAN OpenAI-compatible runtime smoke | Concluido como `PARTIAL` | [AI_CHAT_OLLAMA_LAN_B5B_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5B_REPORT.md) | Provider `ollama-lan` usa `/v1/chat/completions`, allowlist explicita e sem mock fallback; validacao LAN/UI autenticada ficou pendente. |
| `B5-C` AI Chat Ollama LAN authenticated runtime validation | Concluido como `PARTIAL` | [AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md) | Runtime LAN real validado até provider backend; UI autenticada pendente por sessão não persistida. |
| `B5-D` AI Chat authenticated UI session fix/validation | Concluido com `GO` | [AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5D_AUTH_UI_SMOKE.md) | Smoke autenticado same-origin validado; provider `ollama-lan` e baseline `qwen3:1.7b-64k` confirmados na UI. |
| `INFRA-D1` Docker Engine nativo no WSL | Concluido como `PARTIAL` | [WSL_NATIVE_DOCKER_ENGINE_D1_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1_REPORT.md) | Docker atual vem de symlink do Docker Desktop; concluir instalacao nativa com `sudo` interativo. |
| `INFRA-D1B` Docker Engine nativo no WSL com sudo interativo | Concluido como `PARTIAL` | [WSL_NATIVE_DOCKER_ENGINE_D1B_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1B_REPORT.md) | `sudo -v` nao autenticou dentro da PTY desta sessao; nenhuma alteracao de sistema foi aplicada. |
| `INFRA-D1C` Docker Engine nativo no WSL via script root-assistido | Concluido com `GO` | [WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md) | Docker Engine nativo ativo em `/var/lib/docker`; Compose, hello-world, Postgres/Redis, backend e frontend validados. |
| `B5` Hermes/Ollama docs/scripts | Pendente | [HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md) | Manter como docs/diagnóstico, não como runtime default. |
| `B6` Testes/infra | Pendente | [CRITICAL_FIX_ROUND2_TEST_RESULTS.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/CRITICAL_FIX_ROUND2_TEST_RESULTS.md) | Usar apenas em validações isoladas. |

## 5. Índice dos Relatórios

### Relatórios centrais fora de `docs/audit/`

| Documento | Objetivo | Status | Boundary | Manter | Indexar | Atualização mínima |
|---|---|---|---|---|---|---|
| [GENERAL_PROJECT_AUDIT_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/GENERAL_PROJECT_AUDIT_REPORT.md) | Síntese principal da auditoria geral | current | `B1` | sim | sim | apontar para este índice |
| [GENERAL_PROJECT_EDITING_ROADMAP.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/GENERAL_PROJECT_EDITING_ROADMAP.md) | roadmap de edição segura | complementary | `B1/B2/B3/B4` | sim | sim | só pointer cruzado |
| [GENERAL_PROJECT_RISK_REGISTER.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/GENERAL_PROJECT_RISK_REGISTER.md) | registro de riscos | current | `B1` | sim | sim | mínimo, se houver |
| [GENERAL_PROJECT_NEXT_ACTIONS.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/GENERAL_PROJECT_NEXT_ACTIONS.md) | checklist pós-auditoria | complementary | `B1` | sim | sim | apontar para este índice e para a decisão de próxima boundary |
| [WORKTREE_TRIAGE_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WORKTREE_TRIAGE_REPORT.md) | triagem do worktree | current | `B0/B1` | sim | sim | já aponta para `B0`; manter referência ao índice |
| [SECURITY_HYGIENE_B0_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/SECURITY_HYGIENE_B0_REPORT.md) | fechamento do boundary B0 | current | `B0` | sim | sim | manter rotação externa e pointer para `B1` |
| [RELEASE_DOCS_HYGIENE_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/RELEASE_DOCS_HYGIENE_REPORT.md) | higiene de docs/release | current | `B0/B1` | sim | sim | referência cruzada leve |
| [SECURITY_HYGIENE_BOUNDARIES_S1C.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/SECURITY_HYGIENE_BOUNDARIES_S1C.md) | boundaries de hygiene S1-C | current | `B0/B1` | sim | sim | manter como histórico |
| [TRACKED_HYGIENE_CANDIDATES_S1C.txt](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/TRACKED_HYGIENE_CANDIDATES_S1C.txt) | candidatos tracked de higiene | evidence | `B0/B1` | sim | sim | sem atualização funcional |
| [CRITICAL_FIX_ROUND2_MANIFEST.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/CRITICAL_FIX_ROUND2_MANIFEST.md) | manifesto de correções críticas | current | `B2/B4` | sim | sim | apenas pointer cruzado |
| [CRITICAL_FIX_ROUND2_TEST_RESULTS.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/CRITICAL_FIX_ROUND2_TEST_RESULTS.md) | resultados de validação | current | `B2/B4/B6` | sim | sim | apenas pointer cruzado |
| [CSP_HARDENING_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/CSP_HARDENING_REPORT.md) | hardening de CSP | current | `B2` | sim | sim | manter estado/risco residual |
| [AI_CHAT_RATE_LIMIT_REDIS_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_RATE_LIMIT_REDIS_REPORT.md) | rate limit Redis do AI Chat | current | `B2` | sim | sim | manter evidência de Redis/fallback |
| [IMPORT_SERVICE_REFACTOR_MANIFEST.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_SERVICE_REFACTOR_MANIFEST.md) | manifesto da refatoração do import | current | `B3` | sim | sim | manter como histórico da extração progressiva |
| [IMPORT_SERVICE_REFACTOR_PLAN.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_SERVICE_REFACTOR_PLAN.md) | plano de extração progressiva | current | `B3` | sim | sim | manter como histórico; a boundary foi fechada |
| [IMPORT_SERVICE_REFACTOR_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_SERVICE_REFACTOR_REPORT.md) | relatório da refatoração | current | `B3` | sim | sim | manter histórico das extrações |
| [IMPORT_PIPELINE_STAGING_B3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/IMPORT_PIPELINE_STAGING_B3_REPORT.md) | fechamento da boundary B3 | current | `B3` | sim | sim | novo fechamento da boundary |
| [VISUAL_SMOKE_MANUAL_RUNBOOK.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/VISUAL_SMOKE_MANUAL_RUNBOOK.md) | runbook de smoke visual | complementary | `B4` | sim | sim | não transformar em requisito de release sem execução |
| [WSL_NATIVE_DOCKER_ENGINE_D1_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1_REPORT.md) | diagnostico da migracao para Docker Engine nativo no WSL | current | `INFRA-D1` | sim | sim | concluir instalacao com `sudo` interativo |
| [WSL_NATIVE_DOCKER_ENGINE_D1B_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1B_REPORT.md) | tentativa follow-up com sudo interativo | current | `INFRA-D1B` | sim | sim | reexecutar em sessao WSL onde o prompt sudo seja controlavel |
| [WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md) | fechamento da migracao Docker Engine nativo no WSL | current | `INFRA-D1C` | sim | sim | manter como evidencia operacional atual |
| [LOCAL_DOCKER_WSL_NATIVE_RUNBOOK.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/LOCAL_DOCKER_WSL_NATIVE_RUNBOOK.md) | runbook operacional para Docker Engine nativo no WSL | current | `INFRA-D1C` | sim | sim | usar para operacao diaria do runtime nativo |
| [HERMES_GPT_CODEX_CONTEXT_RECOMMENDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_GPT_CODEX_CONTEXT_RECOMMENDATION.md) | recomendação de contexto Hermes | complementary | `B5` | sim | sim | manter como docs |
| [HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md) | recomendação local Ollama | complementary | `B5` | sim | sim | manter como docs |
| [HERMES_OLLAMA_NO_TOOLS_PROVIDER_PROPOSAL.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_OLLAMA_NO_TOOLS_PROVIDER_PROPOSAL.md) | proposta de provider sem tools | proposal | `B5` | sim | sim | não promover como default sem decisão |
| [HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md) | diagnóstico do wrapper Ollama | current | `B5` | sim | sim | manter como diagnóstico |
| [AI_CHAT_OLLAMA_LAN_B5B_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5B_REPORT.md) | fechamento da boundary Ollama LAN OpenAI-compatible | current | `B5-B` | sim | sim | concluir validacao LAN/UI autenticada em B5-C |
| [AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/AI_CHAT_OLLAMA_LAN_B5C_RUNTIME_VALIDATION.md) | validação runtime real do Ollama LAN | current | `B5-C` | sim | sim | fechado pelo smoke autenticado B5-D2 |
| [OLLAMA_LOCAL_MODEL_PROFILE.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/OLLAMA_LOCAL_MODEL_PROFILE.md) | perfil de modelo local | complementary | `B5` | sim | sim | documentação somente |
| [docs/hermesops/HERMES_TOOLS_SKILLS_AUDIT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/hermesops/HERMES_TOOLS_SKILLS_AUDIT.md) | auditoria de skills/ferramentas | current | `B5` | sim | sim | manter como inventário |

### Arquivos canônicos de `docs/audit/`

| Documento | Objetivo | Status | Boundary | Manter | Indexar | Atualização mínima |
|---|---|---|---|---|---|---|
| [ARCHITECTURE_AUDIT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/ARCHITECTURE_AUDIT.md) | visão arquitetural | current | `B1/B2/B4` | sim | sim | se houver síntese nova |
| [AUDIT_ENVIRONMENT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/AUDIT_ENVIRONMENT.md) | ambiente da auditoria | current | `B1` | sim | sim | histórico |
| [BACKEND_AUDIT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/BACKEND_AUDIT.md) | auditoria backend | current | `B2/B3` | sim | sim | histórico |
| [BACKEND_FINDINGS.csv](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/BACKEND_FINDINGS.csv) | findings backend | evidence | `B2/B3` | sim | sim | sem edição funcional |
| [DATABASE_MIGRATIONS_AUDIT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/DATABASE_MIGRATIONS_AUDIT.md) | migrations e DB | current | `B6` | sim | sim | histórico |
| [DATABASE_FINDINGS.csv](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/DATABASE_FINDINGS.csv) | findings DB | evidence | `B6` | sim | sim | sem edição funcional |
| [DESKTOP_APP_AUDIT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/DESKTOP_APP_AUDIT.md) | auditoria desktop | current | `B4/B5` | sim | sim | histórico |
| [DEVOPS_RELEASE_AUDIT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/DEVOPS_RELEASE_AUDIT.md) | release/devops | current | `B0/B6` | sim | sim | histórico |
| [FILE_INVENTORY.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/FILE_INVENTORY.md) | inventário geral | current | `B1` | sim | sim | histórico |
| [FILE_CLASSIFICATION.csv](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/FILE_CLASSIFICATION.csv) | classificação de arquivos | evidence | `B1` | sim | sim | sem edição funcional |
| [FRONTEND_AUDIT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/FRONTEND_AUDIT.md) | auditoria frontend | current | `B4` | sim | sim | histórico |
| [FRONTEND_FINDINGS.csv](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/FRONTEND_FINDINGS.csv) | findings frontend | evidence | `B4` | sim | sim | sem edição funcional |
| [FULL_PROJECT_AUDIT_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/FULL_PROJECT_AUDIT_REPORT.md) | relatório integral | current | `B1` | sim | sim | histórico principal |
| [GAP_ANALYSIS.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/GAP_ANALYSIS.md) | análise de gaps | complementary | `B1/B2/B3/B4/B6` | sim | sim | pode ser resumido futuramente |
| [HIGH_FIX_ROUND3_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/HIGH_FIX_ROUND3_REPORT.md) | correção dos achados HIGH | current | `B2/B4` | sim | sim | histórico |
| [PROJECT_TREE.txt](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/PROJECT_TREE.txt) | árvore do projeto | evidence | `B1` | sim | sim | sem edição funcional |
| [RELEASE_HYGIENE_FINDINGS.csv](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/RELEASE_HYGIENE_FINDINGS.csv) | findings de release | evidence | `B0/B1` | sim | sim | sem edição funcional |
| [SCRIPTS_OPS_AUDIT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/SCRIPTS_OPS_AUDIT.md) | scripts operacionais | current | `B6/B0` | sim | sim | histórico |
| [SCRIPTS_OPS_FINDINGS.csv](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/SCRIPTS_OPS_FINDINGS.csv) | findings de scripts | evidence | `B6/B0` | sim | sim | sem edição funcional |
| [SECURITY_AUDIT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/SECURITY_AUDIT.md) | auditoria de segurança | current | `B0/B2` | sim | sim | histórico |
| [SECURITY_FINDINGS.csv](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/SECURITY_FINDINGS.csv) | findings de segurança | evidence | `B0/B2` | sim | sim | sem edição funcional |
| [TESTING_AUDIT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/TESTING_AUDIT.md) | estratégia de testes | current | `B6` | sim | sim | histórico |
| [TEST_RESULTS.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/TEST_RESULTS.md) | resultados de testes | current | `B6` | sim | sim | histórico |

## 6. Riscos Bloqueadores

- Worktree misto com backend, frontend, testes e documentação ao mesmo tempo.
- Possíveis artefatos sensíveis fora do pacote de docs, exigindo boundary próprio.
- Ollama não deve ser promovido como default sem decisão formal.
- Imports/staging e frontend shell precisam continuar isolados por boundary.

## 7. Próxima Boundary Recomendada

Recomendação objetiva: `B6` se o foco voltar para testes/infra; abrir nova boundary explícita se houver feature ou legado adicional.

Motivo:

- `INFRA-D1` confirmou que o Docker atual ainda depende de Docker Desktop via `/mnt/wsl/docker-desktop`;
- a instalacao nativa nao foi executada porque `sudo -n` nao estava disponivel nesta sessao;
- `INFRA-D1B` tambem parou antes de alteracoes porque `sudo -v` nao autenticou dentro da PTY usada pela ferramenta;
- `INFRA-D1C` concluiu o runtime Docker nativo e validou Postgres, Redis, backend e preview frontend;
- `B2` e `B3` já foram fechados;
- `B4-A` já executou o baseline do frontend shell/UX;
- `B4-A2` já documentou a normalização do runtime;
- `B4-A3` já ativou o runtime WSL nativo e validou o build;
- `B4-B`, `B4-B2` e `B4-B3` documentaram o smoke e suas ressalvas;
- `B4-C` aplicou reparo visual estrutural e gerou screenshots parciais;
- `B4-D` validou o shell autenticado com sessao real, sem burlar autenticacao;
- `B5-C` validou o runtime LAN real e o provider backend, mas ainda precisa do smoke UI autenticado por causa de sessão não persistida no browser.

Se a prioridade de negocio for outra boundary, mantenha a nova boundary explicita e isolada.

## 8. Critérios para Começar Feature Funcional

Antes de uma feature funcional nova:

1. `B1` precisa estar consolidado neste índice.
2. A boundary funcional escolhida precisa ter testes dedicados e escopo isolado.
3. Não pode haver mistura com segredos, docs de release e experimentos de IA.
4. O objetivo funcional precisa caber em um único boundary primário.
5. Mudanças de UX ampla, migrations e infra não devem entrar junto da primeira feature.
