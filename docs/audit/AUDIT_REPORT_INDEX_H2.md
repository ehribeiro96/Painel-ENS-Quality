# Audit Report Index — H2

Boundary: `DOCS-H2 — audit docs consolidation and selective commit`

Este índice define a documentação ativa de auditoria após as boundaries `AUDIT-H1`, `GIT-H2`, `SEC-H2`, `QA-C1` e `QA-C2`. Ele não apaga, move ou renomeia documentação antiga; apenas separa o conjunto ativo do material histórico/deferido.

## Documentos ativos

| Documento | Boundary | Status | Finalidade | Próxima ação | Pode commitar? | Observação |
|---|---:|---|---|---|---|---|
| `README.md` | DOCS-H2 | ACTIVE_INDEX | Entrada curta para leitura humana de auditoria | Manter apontando para este índice | sim | Índice operacional do diretório |
| `NEXT_BOUNDARY_DECISION.md` | DOCS-H2 | ACTIVE_INDEX | Ordem recomendada de próximas boundaries | Atualizar apenas por boundary documental | sim | Não substitui validação funcional |
| `AUDIT_REPORT_INDEX_H2.md` | DOCS-H2 | ACTIVE_INDEX | Índice canônico dos relatórios ativos | Usar como mapa principal | sim | Criado nesta boundary |
| `AUDIT_DOCS_CONSOLIDATION_H2_REPORT.md` | DOCS-H2 | ACTIVE_CURRENT | Relatório de consolidação documental | Referência do commit DOCS-H2 | sim | Criado nesta boundary |
| `SUPERSEDED_AUDIT_DOCS_H2.md` | DOCS-H2 | ACTIVE_INDEX | Lista de docs históricos/superseded/deferidos | Revisar em boundary própria antes de commitar antigos | sim | Criado nesta boundary |
| `HERMES_FULL_PROJECT_AUDIT_H1_REPORT.md` | AUDIT-H1 | ACTIVE_CURRENT | Relatório completo de auditoria H1 | Base para planejamento conservador | sim | H1 ficou PARTIAL por untracked antigos |
| `HERMES_IMPROVEMENT_BACKLOG_H1.md` | AUDIT-H1 | ACTIVE_CURRENT | Backlog de melhorias e riscos | Priorizar por boundary pequena | sim | Não executar em massa |
| `HERMES_DO_NOT_TOUCH_MAP_H1.md` | AUDIT-H1 | ACTIVE_CURRENT | Mapa de áreas proibidas/sensíveis | Consultar antes de qualquer mudança | sim | Do-not-touch operacional |
| `HERMES_RISK_REGISTER_H1.md` | AUDIT-H1 | ACTIVE_CURRENT | Registro de riscos H1 | Atualizar em novas auditorias | sim | Fonte de risco documental |
| `HERMES_NEXT_BOUNDARIES_H1.md` | AUDIT-H1 | ACTIVE_CURRENT | Sugestão de próximas boundaries pós-H1 | Subordinado ao NEXT_BOUNDARY atual | sim | Histórico ainda ativo |
| `GIT_H2_UNTRACKED_SAFETY_TRIAGE_REPORT.md` | GIT-H2 | ACTIVE_CURRENT | Triagem de segurança dos untracked | Usar antes de stage/commit amplo | sim | GIT-H2 ficou PARTIAL por grande volume untracked |
| `GIT_H2_UNTRACKED_INVENTORY.csv` | GIT-H2 | ACTIVE_CURRENT | Inventário CSV dos untracked | Usar para análise metadados-only | sim | Não implica autorização de commit em massa |
| `GIT_H2_UNTRACKED_DECISION_MATRIX.md` | GIT-H2 | ACTIVE_CURRENT | Matriz de decisão dos untracked | Guiar boundaries de limpeza futuras | sim | Não executar remoções nesta boundary |
| `SEC_H2_LOCAL_SENSITIVE_ARTIFACT_TRIAGE_REPORT.md` | SEC-H2 | ACTIVE_SECURITY | Triagem local de artefatos sensíveis | Seguir ações manuais e IGNORE-H2 | sim | GO COM RESSALVAS |
| `SEC_H2_GITIGNORE_PROPOSAL.md` | SEC-H2 | ACTIVE_SECURITY | Proposta de hygiene `.gitignore` | Implementar apenas em IGNORE-H2 | sim | Nesta boundary `.gitignore` não foi alterado |
| `SEC_H2_MANUAL_ACTIONS.md` | SEC-H2 | ACTIVE_SECURITY | Ações humanas para artefatos sensíveis | Revisão humana antes de SEC-H3 | sim | Não abrir conteúdo sensível |
| `POST_COMMIT_VALIDATION_QA_C1_REPORT.md` | QA-C1 | ACTIVE_VALIDATION | Validação pós-commit com ressalva HTTP | Usar como registro parcial | sim | PARTIAL por backend HTTP indisponível |
| `RUNTIME_HTTP_VALIDATION_QA_C2_REPORT.md` | QA-C2 | ACTIVE_VALIDATION | Validação runtime HTTP | Usar como validação principal | sim | GO |

## Segurança/local sensitive

- `SEC-H2` é a referência ativa para artefatos locais sensíveis.
- `GIT-H2` é a referência ativa para triagem dos untracked sem abrir conteúdo proibido.
- Itens que nunca devem ser abertos por agente nesta trilha: `123`, `123.pub`, `.env*`, dumps, bancos locais, tokens, credenciais, `imports/`, screenshots antigas e binários grandes.
- Paths sensíveis podem ser citados por nome/categoria/risco, mas valores não devem ser impressos.

## Validação

- `QA-C1`: `PARTIAL` por backend HTTP indisponível durante a validação pós-commit.
- `QA-C2`: `GO`; relatório runtime HTTP ativo para leitura atual.

## Do-not-touch

- Documento ativo: `HERMES_DO_NOT_TOUCH_MAP_H1.md`.
- Regra operacional: não alterar importação Lansweeper, migrations, Docker/Compose, AI Chat/Ollama, frontend/backend/assets, package-lock, screenshots, `.env*`, dumps ou credenciais dentro de DOCS-H2.

## Backlog

- `HERMES_IMPROVEMENT_BACKLOG_H1.md` contém oportunidades de melhoria.
- `HERMES_NEXT_BOUNDARIES_H1.md` registra a sequência sugerida pela H1.
- O backlog não autoriza execução funcional sem boundary própria.

## Documentos históricos/superseded

Ver `SUPERSEDED_AUDIT_DOCS_H2.md`.

## Ordem recomendada de leitura

1. `README.md`
2. `NEXT_BOUNDARY_DECISION.md`
3. `AUDIT_REPORT_INDEX_H2.md`
4. `HERMES_FULL_PROJECT_AUDIT_H1_REPORT.md`
5. `GIT_H2_UNTRACKED_SAFETY_TRIAGE_REPORT.md`
6. `SEC_H2_LOCAL_SENSITIVE_ARTIFACT_TRIAGE_REPORT.md`
7. `RUNTIME_HTTP_VALIDATION_QA_C2_REPORT.md`
