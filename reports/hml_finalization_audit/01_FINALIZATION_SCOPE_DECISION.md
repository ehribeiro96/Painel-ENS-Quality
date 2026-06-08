# 01 Finalization Scope Decision

## Opção A - Finalizar somente camada HermesOps/HML
Inclui:
- `docs/hermesops/`
- `tools/hermesops_offline/`
- `tools/hmlops_cli/`
- `scripts/hmlops`
- `infra/hermesops/`
- `reports/hml_*`

Risco:
- não fecha o projeto Painel ENS-Quality completo.

## Opção B - Finalizar projeto completo Painel ENS-Quality
Inclui também:
- `backend/`
- `frontend/itam-platform/`
- `docker-compose.yml`
- `requirements*.txt`
- `pyproject.toml`
- `run.py`
- `tests/`
- documentação operacional principal

## Decisão
- A melhor referência de escopo é a **Opção B**.
- Porém, o workspace atual ainda não está consolidado no Git para esse escopo, porque os componentes centrais do app estão untracked.
- Conclusão operacional: **NO-GO para consolidação automática do projeto completo sem aprovação humana do escopo e do baseline**.

