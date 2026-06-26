# Artifact Data Model

The artifact model should remain explicit and minimal.

## Artifact

- `id`: server-generated UUID
- `owner_id`: actor or session owner identifier
- `session_id`: optional conversation/session linkage
- `filename`: sanitized display name
- `content_type`: canonical MIME type
- `size`: byte size
- `sha256`: content hash used for blob addressing
- `source`: provenance label such as `bridge`, `api`, or `manual`
- `created_at`: creation timestamp in UTC

## Derived access record

- `token`: HMAC-signed, short-lived download capability
- `expires_at`: ISO 8601 expiration timestamp
- `artifact_id`: bound artifact identifier
- `owner_id`: bound owner identifier

## Storage split

- metadata lives separately from blob bytes
- blob bytes are content-addressed
- private storage is not publicly mounted
- no direct frontend path to storage root

## Lifecycle notes

- upload creates metadata and blob references together
- signed downloads are time-limited
- delete should honor the retention policy chosen by product/security
