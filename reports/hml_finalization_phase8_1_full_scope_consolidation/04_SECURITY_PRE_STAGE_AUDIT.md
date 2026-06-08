# Security Pre-Stage Audit

## Resultado

- Scan de workspace identificou arquivos proibidos presentes no disco, mas fora da área de release planejada.
- Encontrados: `.env`, `.env.bak_*`, `infra/hermesops/.env.hml`, vários `__pycache__` e `*.pyc`.
- Não houve indício de segredo exposto nos artefatos de texto inspecionados durante esta varredura.

## Classificação

- ` .env.example` e `config/.env.example`: permitidos se mantidos como placeholders.
- `.env`, `.env.hml` e `.env.bak_*`: proibidos no stage e fora do RC.
- `_backup`, `imports`, `exports`, `node_modules`, `.venv` e caches: excluídos do release.

## Evidência

- [04_forbidden_workspace_scan.txt](./evidence/04_forbidden_workspace_scan.txt)

