# Chat Bridge State Contract

This document defines the conversation, run and session state model for the Hermes Chat Bridge adapter.

## State objects

### Conversation

- `conversation_id`
- `owner_id`
- `title`
- `provider`
- `model`
- `created_at`
- `updated_at`
- `last_run_id`
- `last_message_id`
- `status`

### Run

- `run_id`
- `conversation_id`
- `owner_id`
- `session_id`
- `provider`
- `model`
- `status`
- `message_text`
- `streaming`
- `created_at`
- `started_at`
- `completed_at`
- `cancelled_at`
- `error_code`
- `error_message`

### Message

- `message_id`
- `conversation_id`
- `run_id`
- `role`
- `content`
- `provider`
- `model`
- `token_count`
- `created_at`
- `extra_metadata`

### Session binding

The source bridge persists a user-scoped Hermes session id and binds it to the current conversation state.
That state isolation is part of the contract and is owned by the backend, not the frontend.

## Lifecycle

1. `run.created` is emitted when a run record is stored.
2. `run.started` is emitted when the upstream provider session begins.
3. `message.delta` events accumulate until `message.completed` or a terminal event occurs.
4. `tool.call.started` / `tool.call.delta` / `tool.call.completed` are transient tool lifecycle events.
5. `artifact.created` / `artifact.updated` only appear after artifact promotion.
6. `run.completed`, `run.failed` and `run.cancelled` are terminal states.
7. `heartbeat` may continue during long execution windows.

## Ownership rules

- Every conversation and run must be checked against the authenticated owner.
- Event replay must reject foreign run ids.
- Cancellation must only work for the owner of the run.
- Attachments and artifacts inherit the same ownership boundary.

## Streaming fallback

If SSE is unavailable, the same run should still be readable as a JSON snapshot.
The JSON snapshot must preserve `status`, `error_code`, `message` and ownership metadata.
