# M8 - Remove Giant Blob From History

## 1. Status
GO: o blob gigante foi removido do historico local, nenhum blob acima de 100 MiB permanece, o backup local foi criado/verificado, os gates passaram e nenhum push foi executado.

## 2. Objetivo
Remover blob gigante do historico local antes de repetir o push inicial.

## 3. Causa do NO-GO anterior
- Push falhou no pre-receive do GitHub.
- Blob: `docs/audit/m7-pre-push-final-readiness/raw/tree-secret-scan-redacted.log`
- Tamanho antes do rewrite: 4,163,481,600 bytes.

## 4. Backup local
- Bundle: `/home/estevaoqualityadm/projects/_git-history-backups/Painel-ENS-Quality-before-m8-20260629-114538.bundle`
- Verificacao: `git bundle verify` concluiu com bundle OK.

## 5. Rewrite
- Ferramenta: `.venv/bin/python -m git_filter_repo`
- Caminho removido: `docs/audit/m7-pre-push-final-readiness/raw/tree-secret-scan-redacted.log`
- Output: `raw/filter-repo-output.txt`
- Observacao: `git-filter-repo` removeu o remote `origin` por seguranca; o remote real foi restaurado depois.

## 6. Validacao pos-rewrite
- Caminho ainda existe no historico: nao.
- Maior blob restante: 11,700,117 bytes (`assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`).
- Blobs >100 MiB: nenhum.

## 7. Remote
- Origin: `git@github.com:ehribeiro96/Painel-ENS-Quality.git`
- SSH: autenticado como `ehribeiro96`.
- Remote vazio: `git ls-remote --heads origin` nao listou branches.

## 8. Gates
- `git diff --check`: PASS
- `pytest -s -q`: PASS, 336 passed, 22 skipped, 1 warning
- `ruff check backend tests scripts`: PASS
- `compileall`: PASS
- `npm run build`: PASS

## 9. Seguranca
- Segredos nos artefatos M8: nao encontrados.
- StorageState/cookies/tokens commitados: nao.
- Hits por nome em untracked preexistentes com `token` no caminho foram preservados fora do stage e nao sao artefatos M8.

## 10. Push
- Push executado: nao.

## 11. Proxima fase
- `INITIAL_PUSH_AUTHORIZATION_RETRY`
