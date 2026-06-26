# ENS Unified Migration M1B — Artifact Implementation

## 1. Status
GO

## 2. Objetivo
Implementar o mínimo backend seguro para artifacts/anexos no Painel ENS-Quality, sem frontend, sem Docker e sem copiar o services/artifact-server externo.

## 3. Base M1/M5
- M1: contract-only artifact server defined, with upload, list, metadata, download-url and signed download contract.
- M5: recommended path selected as PATH_A_IMPLEMENT_ARTIFACT_FIRST.
- Runtime Apoema: porta 5175, helper scripts/dev-apoema-vite.sh, proxy http://[::1]:8080.

## 4. O que foi implementado
- backend artifacts router registered under /api/v1/artifacts
- secure upload with UploadFile, size limit, MIME allowlist and extension allowlist
- private local storage under data/artifacts/private/
- local metadata manifest under data/artifacts/metadata.json
- server-generated artifact UUIDs
- signed download tokens with HMAC-SHA256 and explicit expiration
- safe download headers with sanitized Content-Disposition
- ownership-based access control with admin override
- delete flow that removes the blob and marks metadata deleted
- download history tracked in metadata without exposing internal paths

## 5. Endpoints criados
- POST /api/v1/artifacts
- GET /api/v1/artifacts
- GET /api/v1/artifacts/{artifact_id}
- GET /api/v1/artifacts/{artifact_id}/download-url
- GET /api/v1/artifacts/download/{signed_token}
- DELETE /api/v1/artifacts/{artifact_id}

## 6. Storage privado
- Blob root: data/artifacts/private/
- Manifest: data/artifacts/metadata.json
- No public static mount for artifact storage
- No internal filesystem path exposed in public DTOs

## 7. Metadata
- id
- owner_user_id
- filename
- content_type
- size_bytes
- sha256
- created_at
- updated_at
- download_count
- deleted_at
- deleted_by
- Internal storage_name exists only in the manifest and is not exposed to the frontend

## 8. Signed URL/HMAC
- HMAC-SHA256 signer implemented in backend/app/services/artifact_signing.py
- Token payload includes artifact_id, owner_user_id, exp and purpose only
- Expiration is short-lived (300s default)
- Signature verification uses constant-time compare

## 9. Auth/RBAC/ownership
- Auth required for upload, list, metadata, download-url and delete
- Ownership enforced at the service layer
- Admin role can view/manage all artifacts
- Download route accepts a signed token and may also accept optional authenticated context

## 10. Limites/allowlists
- Max file size: 10 MiB default
- Allowed extensions: .txt, .csv, .json, .pdf, .png, .jpg, .jpeg, .webp
- Allowed MIME types: text/plain, text/csv, application/json, application/pdf, image/png, image/jpeg, image/webp
- Path traversal filenames are rejected
- Safe filename normalization is applied before storage

## 11. Testes
- tests/test_artifacts_contract.py
- tests/test_artifacts_security_contract.py
- pytest full suite: PASS
- ruff check: PASS
- compileall: PASS
- frontend build: PASS

## 12. O que não foi implementado
- frontend Apoema UI
- Chat Bridge integration
- Designer API integration
- Docker changes
- database migration for artifacts metadata
- vendoring of external services

## 13. Riscos restantes
- Persistent metadata currently lives in a local manifest and can later be migrated to a DB table if authorized.
- Audit logging exists for create/delete/download-url minting, but download access itself is tracked in local metadata history.
- Production rollout may want quota/rate-limit tuning and storage retention policy refinement.

## 14. Próxima fase recomendada
M1C_ARTIFACT_UAT
