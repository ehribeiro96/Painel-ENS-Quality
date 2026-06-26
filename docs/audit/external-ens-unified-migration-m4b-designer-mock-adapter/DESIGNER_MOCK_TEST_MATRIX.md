# Designer Mock Adapter Test Matrix

| Area | Test | Expected |
|---|---|---|
| Router | Designer routes registered | /api/v1/designer paths present in app |
| Auth | GET /health without token | 401 missing_token |
| Auth | GET /templates without token | 401 missing_token |
| Auth | GET /form-options without token | 401 missing_token |
| Auth | POST /banners/json without token | 401 missing_token |
| Allowlist | Unknown template | 422 designer_template_id_not_allowed |
| Allowlist | Unknown canal | 422 designer_canal_not_allowed |
| Allowlist | Unknown kv | 422 designer_kv_not_allowed |
| Mode | Unknown modo_geracao | 422 validation error |
| Size | Prompt > 2000 chars | 422 designer_prompt_too_large |
| Size | Copy > 2000 chars | 422 designer_copy_too_large |
| Determinism | Same payload twice | Same job body returned |
| Ownership | Viewer reads admin job | 403 designer_permission_denied |
| Mutation | Adjust item | Item adjusted_count increments |
| Mutation | Refresh item URL | Item refresh_count increments |
| Mutation | Cancel job | Job becomes cancelled |
| Blocked path | POST /banners | 501 designer_feature_blocked |
| Blocked path | GET /download-url | 409 designer_feature_blocked |
| Security | DTOs expose no provider keys/paths | No provider_key/internal_path fields or serialized values |
| Frontend | No direct provider call | Frontend files only call backend API base |
