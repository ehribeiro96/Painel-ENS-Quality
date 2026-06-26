# Designer Provider Isolation Contract

## Principle
Provider selection, model selection, timeouts, retries, and safety gates are backend-owned. The frontend must never call Gemini, Imagen, Vertex, OpenAI, Ollama, or any other provider directly.

## External evidence
- `main.py` reads `GEMINI_API_KEY` / `GOOGLE_API_KEY` from env and constructs the GenAI client server-side
- `api/app.py` exposes only HTTP DTO endpoints
- `api/supabase_outputs.py` keeps storage credentials server-side

## Target rules
- SERVER_SIDE_PROVIDER_KEYS_ONLY
- NO_DIRECT_FRONTEND_PROVIDER_CALL
- content policy gate before any provider call
- explicit prompt sanitization and output redaction
- per-job/provider rate limits and quotas
- audit log every provider-backed action

## Notes
This phase intentionally does not implement a live provider adapter. The contract only defines the backend isolation boundary and the approvals required before any real generation is enabled.
