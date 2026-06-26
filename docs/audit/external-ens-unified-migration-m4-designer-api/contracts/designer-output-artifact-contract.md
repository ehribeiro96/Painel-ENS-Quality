# Designer Output Artifact Contract

## Purpose
Designer outputs become Artifact M1 records, not public static files. The external app currently writes to local `outputs/` and optionally mirrors to Supabase; that is not the target design.

## Required behavior
- store generated assets in private artifact storage
- create a download URL only through the Artifact contract
- persist metadata (job, item, owner, mime, size, ttl)
- support cleanup on cancel/failure/expiry
- keep signed URLs short-lived

## Blockers
Because M1 is still `M1A_CONTRACT_ONLY`, live storage, download minting, and cleanup remain blocked until the Artifact implementation exists.

## Safety terms
PRIVATE_OUTPUT_STORAGE, SIGNED_DOWNLOAD_URL, SAFE_DOWNLOAD, ARTIFACT_OWNERSHIP_CHECK.
