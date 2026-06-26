# Chat Bridge Event Contract

This contract defines the event envelope and the canonical run lifecycle for the Hermes Chat Bridge adapter.

## Event envelope

Events are normalized to a compact payload with at least:

- `event`
- `run_id`
- `conversation_id`
- `session_id`
- `message_id` when a message is finalized
- `tool_call_id` when a tool is in flight
- `artifact_id` when a file is promoted to artifact storage
- `data` for event-specific details

## Canonical target events

- `run.created`
- `run.started`
- `message.delta`
- `message.completed`
- `tool.call.started`
- `tool.call.delta`
- `tool.call.completed`
- `artifact.created`
- `artifact.updated`
- `run.completed`
- `run.failed`
- `run.cancelled`
- `error`
- `heartbeat`

## Source alignment notes

The inspected bridge already normalizes several upstream forms:

- `run.created` is emitted as a meta event when the run is persisted.
- `message.delta`, `assistant.delta` and `response.output_text.delta` collapse into `message.delta`.
- `message.completed`, `assistant.completed`, `run.completed`, `response.completed` and `response.output_item.done` are collapsed into terminal completion events.
- `run.failed`, `response.failed` and `error` collapse into failure handling.
- `tool.completed` currently exists in source form and is mapped here to `tool.call.completed`.
- `status` is used as the heartbeat/progress lane when the run is still active.

## Streaming rules

1. Streaming is preferred for live runs.
2. JSON fallback must still preserve the same terminal semantics.
3. Heartbeat events should be emitted while the upstream run is still active.
4. Cancellation must stop new deltas and finalize the run as `run.cancelled`.
5. `artifact.created` and `artifact.updated` must only appear after the artifact contract is available.

## Safety rules

- Never emit raw provider secrets.
- Never echo untrusted attachment text as trusted system content.
- Never expose internal session identifiers beyond the ownership boundary.
- Never expose raw storage paths.
- Keep tool names on an allowlist.
