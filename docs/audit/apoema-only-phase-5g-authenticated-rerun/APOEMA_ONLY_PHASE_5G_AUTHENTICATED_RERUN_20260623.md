# Apoema-only Phase 5G Authenticated Rerun — 2026-06-23

## 1. Status
PARTIAL-GO

## 2. Auth mode usado
MANUAL_LOGIN attempted; no secure session was completed in this runtime.

## 3. Sessão autenticada validada
Nao

## 4. StorageState ficou fora do repo
Sim

## 5. Credenciais impressas
Nao

## 6. Rotas protegidas redirecionaram para login
Sim, porque a sessao segura nao foi concluida

## 7. Screenshots autenticados criados
Nao

## 8. Viewports auditados
390x844, 768x1024, 1366x768, 1440x900, 1920x1080

## 9. Rotas auditadas
/login only as rendered entry point; protected routes were not validated under auth

## 10. P0/P1/P2/P3
0 / 0 / 0 / 0

## 11. Chat autenticado
Nao testado

## 12. Ativos/detalhe
Nao testado

## 13. Usuarios/detalhe
Nao testado

## 14. Settings
Nao testado

## 15. Mobile
Baseline only; authenticated pass blocked

## 16. Desktop
Baseline only; authenticated pass blocked

## 17. Validações
Reuse of previous 5G technical gates: unittest, ruff, compileall, frontend build, git diff --check, smoke HTTP all passed previously. This rerun did not add code changes.

## 18. Segurança
No credential values were printed. No storageState was committed.

## 19. Limitações
No safe credential or storageState was available, and manual login could not be completed in the available runtime.

## 20. Próxima fase recomendada
Provide a secure temporary storageState or a usable local UAT credential and rerun the authenticated capture.
