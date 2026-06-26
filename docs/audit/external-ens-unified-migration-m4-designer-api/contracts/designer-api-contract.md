# Designer API Contract

## Scope
Backend-owned contract for the optional Designer module in Painel ENS-Quality / Apoema. The external source analyzed is `apps/designer-api`, but this phase is contract-only because provider keys, output storage, and job ownership are not safe to promote directly.

## External evidence
- External root: `/tmp/ens-unificado-analysis/projeto-ens-unificado-main/apps/designer-api`
- Core files: `main.py`, `api/app.py`, `api/job_service.py`, `api/supabase_outputs.py`, `execution/select_template.py`, `execution/prompts.py`
- External routes include `GET /health`, `POST /banners`, `POST /banners/json`, `GET /templates`, `GET /banners/form-options`, `GET /banners/{job_id}`, `GET /banners/{job_id}/download`, `POST /banners/{job_id}/items/{item_id}/adjust`, and `POST /banners/{job_id}/items/{item_id}/refresh-url`.

## Target shape
- `GET /api/v1/designer/health`
- `GET /api/v1/designer/templates`
- `GET /api/v1/designer/form-options`
- `POST /api/v1/designer/banners`
- `POST /api/v1/designer/banners/json`
- `GET /api/v1/designer/jobs/{job_id}`
- `GET /api/v1/designer/jobs/{job_id}/download-url`
- `POST /api/v1/designer/jobs/{job_id}/items/{item_id}/adjust`
- `POST /api/v1/designer/jobs/{job_id}/items/{item_id}/refresh-url`
- `POST /api/v1/designer/jobs/{job_id}/cancel`

## Mandatory controls
AUTH_REQUIRED, RBAC_REQUIRED, JOB_OWNERSHIP_CHECK, SERVER_SIDE_PROVIDER_KEYS_ONLY, NO_DIRECT_FRONTEND_PROVIDER_CALL, TEMPLATE_ALLOWLIST, PROMPT_INPUT_VALIDATION, PRIVATE_OUTPUT_STORAGE, SIGNED_DOWNLOAD_URL.

## Decision
This phase is `M4A_CONTRACT_ONLY`. The design intentionally avoids frontend provider exposure and defers live generation until Artifact M1, Chat Bridge M2, and RAG M3 are implemented safely.

## Integration notes
- Outputs are future artifact records, not public `/files` paths.
- Prompt assistance is optional and must be backend-owned.
- The frontend only consumes `/api/v1/designer` DTOs.
