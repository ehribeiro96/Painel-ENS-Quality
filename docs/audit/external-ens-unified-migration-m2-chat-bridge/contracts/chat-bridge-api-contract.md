# Chat Bridge API Contract

This document defines the backend-owned contract for the Hermes Chat Bridge adapter.
The Apollo / Apoema frontend must only consume `/api/v1`; it must not call Hermes, Ollama, Composio or the artifact server directly.

## Target endpoints

- `POST /api/v1/ai-chat/conversations`
- `GET /api/v1/ai-chat/conversations`
- `GET /api/v1/ai-chat/conversations/{conversation_id}`
- `POST /api/v1/ai-chat/runs`
- `GET /api/v1/ai-chat/runs/{run_id}`
- `GET /api/v1/ai-chat/runs/{run_id}/events`
- `POST /api/v1/ai-chat/runs/{run_id}/cancel`
- `POST /api/v1/ai-chat/runs/{run_id}/attachments`
- `GET /api/v1/ai-chat/providers`

## Contract rules

1. AUTH_REQUIRED for every conversation/run management endpoint.
2. RBAC_REQUIRED for mutation endpoints and any future operator tools.
3. SERVER_SIDE_PROVIDER_KEYS_ONLY: provider secrets stay in the backend.
4. NO_DIRECT_FRONTEND_PROVIDER_CALL: the frontend never receives Hermes, Ollama or Composio credentials.
5. `GET /api/v1/ai-chat/runs/{run_id}/events` may use SSE (`text/event-stream`) with a JSON fallback for contract-only mode.
6. `POST /api/v1/ai-chat/runs` must support a non-streaming JSON fallback first.
7. `POST /api/v1/ai-chat/runs/{run_id}/attachments` is BLOCKED_UNTIL_ARTIFACT_IMPLEMENTATION until M1 leaves contract-only status.
8. Every durable mutation should produce audit evidence and preserve ownership isolation.

## Provider boundaries

Provider selection is backend-owned and should be returned by the `/providers` endpoint.
The UI must not hardcode provider names, base URLs or token locations.

## Error handling

- User-facing errors must be sanitized.
- Upstream provider details should be truncated and redacted.
- Rate limit errors must be explicit and retryable.
- Validation errors must be DTO-based and stable.
