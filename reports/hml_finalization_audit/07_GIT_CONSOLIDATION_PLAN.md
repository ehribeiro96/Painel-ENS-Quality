# 07 Git Consolidation Plan

## O que deve entrar no baseline final
- `infra/hermesops/`
- `docs/hermesops/`
- `tools/hmlops_cli/`
- `tools/hermesops_offline/`
- `scripts/hmlops`
- documentação operacional principal
- `backend/`, `frontend/itam-platform/`, `tests/`, `requirements*.txt`, `pyproject.toml`, `docker-compose.yml`, `run.py`, se e somente se o escopo completo for aprovado por humano

## O que deve ficar untracked/ignored
- `.env`
- `.env.hml`
- `_backup/`
- `imports/`
- `exports/`
- `node_modules/`
- `__pycache__/`
- `.pyc`
- caches e builds locais

## O que é lixo de export/import/backup
- backups históricos em `_backup/`
- artefatos importados em `imports/`
- exportações em `exports/`
- caches Python/Node

## Estado atual
- Nenhum arquivo foi staged.
- Nenhum commit foi criado.
- O baseline ainda não foi consolidado para o escopo completo.

## Conclusão
- A consolidação automática do Git para o projeto completo precisa de aprovação humana explícita.

