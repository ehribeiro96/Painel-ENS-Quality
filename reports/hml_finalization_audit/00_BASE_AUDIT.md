# 00 Base Audit

## Workspace
- Workspace: `/home/estevaoqualityadm/projects/Painel-ENS-Quality`
- Branch: `main`
- HEAD: `4c62932d48b7a032e4aaa7ee0cbfa53d2894f93e`
- Commit range recente confirma um baseline antigo, com muita atividade fora do Git atual.

## Observações principais
- O workspace contém um conjunto muito grande de itens untracked.
- `backend/`, `frontend/`, `docker-compose.yml`, `requirements*.txt`, `pyproject.toml`, `run.py` e `tests/` estão presentes no disco, mas não estão versionados.
- `infra/hermesops/`, `docs/hermesops/`, `tools/hmlops_cli/`, `tools/hermesops_offline/` e `scripts/hmlops` já estão rastreados.
- Há diretórios de trabalho, backup e exportação fora do baseline de release, incluindo `_backup/`, `imports/`, `exports/`, `frontend/itam-platform/node_modules`, `frontend/itam-platform/dist`, `.venv`, `.ruff_cache` e `__pycache__`.

## Leitura de auditoria
- O repositório não representa apenas a camada HermesOps/HML; ele contém artefatos do projeto completo e um volume grande de material ainda não consolidado no Git.
- O estado atual é suficiente para auditoria e pacote limpo de release, mas não para considerar o workspace já consolidado como baseline final do projeto completo.

