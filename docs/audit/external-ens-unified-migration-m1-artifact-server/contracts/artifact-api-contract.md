# Artifact API Contract

This document defines the safe target contract for artifact handling in Painel ENS-Quality / Apoema.
It is intentionally backend-owned: the frontend must never receive raw storage paths or direct storage credentials.

## Core endpoints

- `POST /api/v1/artifacts`
- `GET /api/v1/artifacts`
- `GET /api/v1/artifacts/{artifact_id}`
- `GET /api/v1/artifacts/{artifact_id}/download-url`
- `GET /api/v1/artifacts/download/{signed_token}`
- `DELETE /api/v1/artifacts/{artifact_id}`

## Contract rules

1. Authentication is required for all management endpoints.
2. RBAC is required for upload/delete and any future management actions.
3. The backend generates artifact IDs and signed tokens server-side.
4. The frontend never sees private storage paths, secret keys, or direct filesystem handles.
5. Download URLs must expire quickly and be HMAC signed.
6. Binary content must be streamed from backend storage only.
7. All lifecycle mutations must produce audit evidence.

## Response shape

Artifact DTOs should be explicit and stable, for example:

- `id`
- `owner_id`
- `session_id`
- `filename`
- `content_type`
- `size`
- `sha256`
- `created_at`
- `source`
- `content_url` or `download_url` only when safe to expose

## Security requirements

- private storage only
- safe filename handling
- MIME/extension allowlists
- upload size limits
- signed URL expiration
- constant-time signature comparison
- audit logging for upload, access-link minting, download, and delete
