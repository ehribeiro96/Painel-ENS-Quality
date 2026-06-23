# Local Release Readiness — 2026-06-23

## 1. Status
GO/PARTIAL-GO/NO-GO: PARTIAL-GO

## 2. Contexto
Commits validados:
- 0ef3b2a feat(frontend): add Apoema preview experience
- d22c432 fix(frontend): improve Apoema responsive density
- bd9120ef feat(apoema): connect ai chat backend and safe fallback
- 283d9bc fix(security): harden p0 p1 production blockers
- 870ec99 docs(audit): triage untracked repository artifacts
- eb8011f chore(repo): add untracked artifact safety boundary
- ebf8284 chore(repo): define legacy and artifact boundary

## 3. Git
- Branch: `main`
- Stage: empty
- Untracked: many preexisting artifact-boundary files remain untracked, plus local audit docs created for this task
- Push: not executed

## 4. Gates executados
| Gate | Status | Observação |
|---|---|---|
| unittest | PASS | `177` testes executados, `8` skipped |
| ruff | PASS | sem erros |
| compileall | PASS | sem erros |
| npm run build | PASS | bundle frontend gerado com sucesso |
| docker compose config | PASS | configuração renderizada com sucesso |
| git diff --check | PASS | sem whitespace / patch issues |

## 5. Segurança
- .env real versionado: não
- secrets/chaves versionadas: não
- /metrics protegido: sim
- Apoema routes protegidas: sim
- ai-chat auth/RBAC: sim
- frontend chama Ollama direto: não

## 6. .gitignore e artefatos locais
- exports: validado
- _validation: validado
- reports: validado
- screenshots: validado
- dist/cache: validado
- legacy source maps: validado

## 7. Smoke opcional
- /apoema-preview: respondeu `200 OK` no frontend Vite já rodando
- /apoema: respondeu `200 OK` no frontend Vite já rodando
- /health/ready: timeout, backend não estava disponível neste runtime
- /api/v1/ai-chat/providers sem token: timeout, backend não estava disponível neste runtime

## 8. Riscos restantes
- untracked preexistentes: há muitos artefatos já presentes no worktree, mas o boundary e o `.gitignore` cobrem os padrões críticos verificados
- METRICS_TOKEN precisa ser configurado fora de local: o endpoint segue protegido por token quando configurado
- ambientes que dependiam de APP_AUTO_MIGRATE devem configurar explicitamente: a validação de compose mostra `APP_AUTO_MIGRATE=0`
- chunk grande Vite ainda não otimizado: o build passou, mas o bundle principal continua grande

## 9. Decisão
PARTIAL-GO

## 10. Próxima fase recomendada
Fechar o release somente depois de um smoke autenticado com backend disponível e, se a política de release exigir árvore limpa, reconciliar os edits locais preexistentes antes de promover o ambiente.
