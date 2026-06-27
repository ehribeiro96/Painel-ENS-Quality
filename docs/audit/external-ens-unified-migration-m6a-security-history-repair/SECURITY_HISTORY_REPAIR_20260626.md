# M6A Security History Repair + Auth State Regen

## 1. Status
PARTIAL-GO:

## 2. Motivo da fase
Um valor sensivel de sessao apareceu em commit local nao enviado. A prioridade foi reparar o historico local antes de qualquer tentativa futura de envio ao remoto.

## 3. Commits afetados
- Antes: `d9309da` continha evidencia M6 com valor sensivel em JSON bruto.
- Redaction posterior antes do repair: `5350527`.
- Depois do rewrite: `3be8c92` substitui o commit M6 original ja com evidencia redigida.
- O commit anterior de redaction ficou vazio e foi descartado pelo rebase controlado.

## 4. Revogacao/rotacao
- Status: nao confirmado.
- Observacao: o valor era de sessao UAT/local. Sem acesso a credencial local ou painel externo nesta boundary, a invalidacao formal nao pode ser comprovada. Push deve permanecer bloqueado ate confirmacao operacional.

## 5. Estrategia de repair
- Ferramenta preferida indisponivel: `git-filter-repo` nao instalado.
- Ferramenta usada: rebase local controlado com edicao do commit afetado.
- Escopo: commits locais em `origin/main..HEAD`, sem push.
- Push executado: nao.

## 6. Resultado do scan de historico
- Antes: scanner amplo encontrou 459 padroes, incluindo 1 JWT real no commit M6 original e muitos falsos positivos documentais/codigo/binarios.
- Depois: scanner amplo encontrou 458 padroes, com `JWT_FINDINGS_AFTER=0`.
- Validacao exata: o JWT real e o link assinado real foram removidos do historico local reescrito. Achados remanescentes da validacao exata foram o endpoint contratual de download de artefatos, classificado como falso positivo documental.

## 7. StorageState UAT
- Criado: nao.
- Local esperado: `/tmp/apoema-uat-auth-state.json`.
- Commitado: nao.
- Motivo: nao havia `APOEMA_UAT_EMAIL`, `APOEMA_UAT_USER`, `APOEMA_UAT_PASSWORD` nem `/tmp/painel_runtime_h5_credentials.txt` no ambiente.

## 8. Playwright autenticado
- Refresh: nao executado.
- Redirect: nao testado.
- Resultado: bloqueado por ausencia de storageState.

## 9. Seguranca
- Tree M6 atual redigido.
- O scan atual da pasta de repair nao encontrou padroes de segredo real.
- Untracked preexistentes foram preservados.
- Nenhum arquivo de sessao foi colocado no repositorio.

## 10. Validacoes
- `git diff --check`: PASS.
- `pytest -s tests`: PASS, 325 passed, 22 skipped, 1 warning.
- `ruff check backend tests scripts`: PASS.
- `compileall`: PASS.
- `npm run build`: PASS.

## 11. Limitacoes
- Sem `git-filter-repo`, o repair foi feito por rebase local controlado.
- Sem credencial UAT local, nao foi possivel regenerar storageState nem reexecutar Playwright autenticado.
- A invalidacao/rotacao da sessao anterior nao foi confirmada.

## 12. Proxima fase recomendada
`M6_AUTHENTICATED_E2E_RERUN` somente depois de provisionar credencial UAT local segura e confirmar invalidacao da sessao antiga.
