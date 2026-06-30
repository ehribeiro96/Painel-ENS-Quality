# SMTP Credential Rotation Required

ENS_SMTP_PASSWORD was detected in versioned repository content.

Required external action:
- Revoke or rotate the SMTP credential in the provider/environment where it is valid.
- Do not reuse the exposed value.
- Store the replacement only in a proper secret manager or deployment environment.
- Do not commit the replacement to Git.

Status:
- Rotation status: NOT VERIFIED BY CODEX
