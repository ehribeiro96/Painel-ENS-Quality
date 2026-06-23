# API Contract Audit — Deep Project Audit 2026-06-23

## Escopo

Comparação entre `frontend/itam-platform/src/lib/api.ts`, `lib/types.ts`, schemas backend e rotas em `backend/app/api/v1/routes/`.

## Contratos alinhados (amostra verificada)

| Frontend (`api.ts`) | Backend | Status |
|---------------------|---------|--------|
| `POST /auth/login` | `auth.py` | OK |
| `POST /auth/refresh` | cookie HttpOnly | OK |
| `GET /assets?page_size=` | `Page[AssetRead]` | OK |
| `POST /assets/{id}/move` | `MovementRead` | OK |
| `GET /assets/{id}/history` | `list[MovementRead]` enriquecido | OK |
| `POST /imports/spreadsheet/upload` | multipart `file`, `import_mode` | OK |
| `POST /imports/{id}/mapping` | `ImportMappingUpdate` | OK |
| `POST /imports/{id}/apply` | `ImportApplyResponse` | OK |
| `GET /macros/templates` | `list[MacroTemplateRead]` | OK |
| `POST /macros/generate` | `MacroGenerationRead` | OK |
| `GET /movements/{id}/suggested-macro` | `SuggestedMovementMacro` | OK |
| `GET /ai-chat/conversations` | `list[AiChatConversationRead]` | OK |
| `POST /ai-chat/conversations/{id}/messages` | `AiChatConversationDetail` | OK |
| Apoema `GET /ai-chat/providers` | `ApoemaChatProvidersResponse` | OK (auth requerida) |
| Apoema `POST /ai-chat/message` | `ApoemaChatMessageResponse` | OK (auth requerida) |

## Inconsistências

### API-001 — Apoema trata erro HTTP como sucesso mock (P1)
- Frontend: `apoemaChatApi.ts` não inspeciona status antes do fallback
- Backend: retorna 401/403/429/502 com `detail` JSON
- Impacto: contrato de erro ignorado no cliente Apoema

### API-002 — `dashboardSummary` tipado como `Record<string, number>` (P3)
- Backend pode retornar chaves adicionais; frontend normaliza parcialmente em `DashboardPage`
- Risco baixo; defensive coding presente

### API-003 — Assinaturas retornam HTML string (INFO)
- `api.signaturePreview` usa `accept: text/html` — alinhado com `HTMLResponse`
- Sem inconsistência funcional

### API-004 — `enableAiChat` build-time vs `enable_ai_chat` runtime (P2)
- Backend força `enable_ai_chat=true` em local
- Frontend flag `ENABLE_AI_CHAT` não usada no menu
- Usuário pode ver menu IA enquanto backend retorna `ai_chat_disabled` em outros ambientes

### API-005 — Import upload: frontend não pré-valida extensão (P3)
- Backend rejeita com `unsupported_import_file`
- UX depende de round-trip; aceitável

## Tratamento de status HTTP no cliente principal

| Status | `api.ts` | Comportamento |
|--------|----------|---------------|
| 401 | refresh + `handleUnauthorized` | OK no cliente principal |
| 403 | `ApiError` | OK |
| 422 | `ApiError` com detail | OK |
| 502/503 | `ApiError` | OK em AiChatPage |

Apoema client **não** reutiliza `api.ts` request wrapper — duplicação de contrato.

## Recomendações

1. Reutilizar `request()` de `api.ts` no Apoema ou extrair cliente HTTP compartilhado.
2. Unificar mapeamento de erros AI entre `AiChatPage` e `ChatPage` Apoema.
3. Tipar `dashboardSummary` com interface explícita compartilhada.
