# Security Hygiene B0 Report

## 1. Resumo executivo
O boundary `B0 — Segurança/higiene` foi concluído sem commit.

O candidato forte a segredo em [tools/composio_client.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tools/composio_client.py) foi removido do código e substituído por carregamento obrigatório via `COMPOSIO_API_KEY` no ambiente. O script agora falha com mensagem clara se a variável não existir.

## 2. Arquivo sensível tratado
- [tools/composio_client.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tools/composio_client.py)

## 3. O que foi alterado
- Removido o fallback hardcoded de API key.
- Introduzido `_require_composio_api_key()` para exigir `COMPOSIO_API_KEY` no ambiente.
- Mantido o comportamento mínimo do client.
- Adicionada ignorância explícita de [/.vscode/settings.json](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.vscode/settings.json) em [/.gitignore](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.gitignore).
- Registrado o fechamento do boundary em [docs/WORKTREE_TRIAGE_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WORKTREE_TRIAGE_REPORT.md).

## 4. O que não foi alterado
- Nenhuma área funcional de backend ou frontend fora do B0.
- Nenhuma migration.
- Nenhum dado UAT.
- Nenhum `.env` foi lido.
- Nenhum Docker foi executado.
- Nenhum commit foi feito.

## 5. Se chave real foi removida
O valor hardcoded foi removido do código e substituído por variável de ambiente.

Se a chave antiga era real, ela deve ser considerada comprometida e tratada externamente como rotação obrigatória.

## 6. Nota obrigatória sobre rotação
`COMPOSIO_API_KEY` deve ser rotacionada fora do repositório se a credencial anterior era válida em qualquer ambiente real.

## 7. Regras de ignore verificadas/ajustadas
- [/.gitignore](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.gitignore) já continha cobertura para `.env`, `.env.*`, `secrets/`, `credentials/`, dumps, bancos e backups.
- Foi adicionada cobertura explícita para `.vscode/settings.json`.
- [/.dockerignore](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.dockerignore) já cobria `.vscode/`, `.env`, `secrets/`, `credentials/`, dumps, bancos e backups.
- Não foi adicionada ignorância ampla para `docs/`.

## 8. Scanner redigido antes/depois
### Antes
- `11` hits totais.
- `1` candidato forte a segredo: `tools/composio_client.py` linha aproximada `17`.
- Classificação: risco real até correção.

### Depois
- `12` hits totais.
- `1` hit resolvido: `tools/composio_client.py:22` com `COMPOSIO_API_KEY` vindo do ambiente.
- `11` hits restantes classificados como falso positivo ou placeholder redigido, incluindo:
  - `docs/HERMES_OLLAMA_WRAPPER_DIAGNOSTIC.md` placeholder redigido
  - `docs/WORKTREE_TRIAGE_REPORT.md` placeholder redigido
  - `assets/legacy/Laravel/*` por nomes genéricos como `token` e `password`
  - `assets/static/vendor/tpl/*` por padrões genéricos como `sk-` e `password`
  - `.github/workflows/docker-build-push.yml` por referência a `secrets.GITHUB_TOKEN`

## 9. Validações executadas
- `PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app backend/alembic tests scripts tools` -> `PASS`
- `timeout 120 .venv/bin/python -m ruff check tools/composio_client.py` -> `PASS`
- `PYTHONPATH=backend timeout 120 .venv/bin/python -m ruff check backend tests scripts tools` -> `FAIL` por ruído legado amplo fora do B0 em `tools/hermesops_offline/*` e `tools/hmlops_cli/*`

## 10. Riscos remanescentes
- O repositório ainda contém muitos hits de scanner com baixa confiança em documentação, workflow e legado.
- O `ruff` global continua falhando por legado fora do B0; isso não invalida a correção do arquivo tratado.
- `tools/composio_client.py` permanece untracked até decisão futura de versionamento.

## 11. Arquivos alterados
- [tools/composio_client.py](/home/estevaoqualityadm/projects/Painel-ENS-Quality/tools/composio_client.py)
- [/.gitignore](/home/estevaoqualityadm/projects/Painel-ENS-Quality/.gitignore)
- [docs/WORKTREE_TRIAGE_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WORKTREE_TRIAGE_REPORT.md)
- [docs/SECURITY_HYGIENE_B0_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/SECURITY_HYGIENE_B0_REPORT.md)

## 12. Próximo passo recomendado
1. Deixar `tools/composio_client.py` fora do caminho funcional até haver decisão explícita de versionamento.
2. Se o `COMPOSIO_API_KEY` antigo era válido em qualquer ambiente real, fazer rotação externa imediata.
3. Consultar o índice operacional em [docs/audit/README.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/README.md) e a decisão em [docs/audit/NEXT_BOUNDARY_DECISION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/NEXT_BOUNDARY_DECISION.md) antes da próxima boundary funcional.
