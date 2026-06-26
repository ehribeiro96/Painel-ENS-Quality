# Designer Job Contract

## Core job model
A Designer job is server-owned and job IDs are generated on the backend. The external app currently keeps jobs in memory and may persist to Supabase when enabled; the target must move to explicit ownership and audited persistence.

### Target states
- `queued`
- `running`
- `completed`
- `failed`
- `cancelled`
- `expired`

### External states observed
- `pending`
- `running`
- `done`
- `partial_done`
- `failed`

## Ownership
- `job.owner_user_id` is mandatory in the target
- job mutations require ownership checks
- item adjustments require the same owner as the job

## Required fields
- `job_id`
- `status`
- `created_at`
- `updated_at`
- `requested_by` / `owner_user_id`
- `progress`
- `items[]`
- `error` (redacted)

## Cancellation semantics
- Cancelling a job transitions it to `cancelled`
- In-flight work must stop server-side
- Artifact cleanup is triggered through the Artifact contract

## Safety
- No provider payload is returned to the frontend
- Errors must be summarized, not leaked raw
- Job data must be audit logged
