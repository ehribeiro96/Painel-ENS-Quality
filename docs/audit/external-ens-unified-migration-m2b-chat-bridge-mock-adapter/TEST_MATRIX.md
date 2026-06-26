# M2B Chat Bridge Mock Adapter — Test Matrix

| Area | File / command | What it proves |
|---|---|---|
| Backend mock provider | `tests/test_ai_chat_provider_mock.py` | Mock provider is deterministic, offline, and does not rely on external keys or network calls. |
| Backend API contract | `tests/test_ai_chat_api.py` | `/ai-chat/*` routes require auth, persist conversations/messages, reject oversized payloads, and sanitize provider errors. |
| Backend hardening | `tests/test_ai_chat_hardening.py` | Feature flag behavior, safe metadata, rate limiting, and frontend safety notice coverage. |
| Apoema backend bridge | `tests/test_apoema_ai_chat_backend.py` | Mock provider catalog and `generate_apoema_message()` return the expected contract with safe fallback behavior. |
| Chat bridge MVP contract | `tests/test_ai_chat_mvp.py` | Provider selection, settings defaults, and payload limits remain aligned with the contract. |
| Frontend chat UX | `frontend/itam-platform/src/apoema/pages/ChatPage.tsx` | UI now states when the mock adapter is active and when fallback local mode is in use. |
| Frontend API bridge | `frontend/itam-platform/src/apoema/lib/apoemaChatApi.ts` | Chat requests are sent to `/api/v1/ai-chat/message` and offline fallback is explicit. |
| Whole-suite verification | `PYTHONPATH=backend .venv/bin/python -m pytest` | Repository-wide regression confidence. |
| Static checks | `.venv/bin/python -m ruff check backend tests scripts` | Lint boundaries stay clean. |
| Bytecode compile | `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts` | Import and syntax integrity of Python sources. |
| Frontend build | `cd frontend/itam-platform && PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build` | TypeScript and Vite build remain green after the bridge change. |

## Notes

- The contract remains backend-owned.
- No real provider integration was introduced.
- The local fallback path is still present by design for network failure, but it is clearly labeled.
- The mock adapter remains the explicit UAT path for this phase.
