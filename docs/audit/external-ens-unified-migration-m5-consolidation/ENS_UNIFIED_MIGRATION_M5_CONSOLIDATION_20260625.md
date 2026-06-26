# ENS Unified Migration M5 — Consolidation Decision

## 1. Status
GO

## 2. Objetivo
Consolidar M0–M4 e decidir a primeira implementação real da migração ENS Unificado para Apoema.

## 3. Base de fases
- M0: GO, plano mestre, runtime sem alteração, módulos aprovados: artifact-server/chat-bridge/rag-mcp/designer-api.
- M1: PARTIAL-GO, M1A_CONTRACT_ONLY, Artifact Server contract definido, backend/frontend/docker sem alteração.
- M2: PARTIAL-GO, M2A_CONTRACT_ONLY, Chat Bridge contract definido, streaming/SSE/cancelamento/heartbeat definidos, backend/frontend/docker sem alteração.
- M3: PARTIAL-GO, M3A_CONTRACT_ONLY, RAG MCP contract definido, tools e collections mapeadas, backend/frontend/docker sem alteração.
- M4: PARTIAL-GO, M4A_CONTRACT_ONLY, Designer API contract definido, jobs/templates/opções/provider isolation mapeados, backend/frontend/docker sem alteração.

## 4. Estado runtime
- Porta: 5175
- Helper: scripts/dev-apoema-vite.sh
- Proxy: http://[::1]:8080
- URL Windows: http://127.0.0.1:5175/apoema

## 5. Resumo executivo
- Migração direta: não permitida nesta fase.
- Primeira implementação recomendada: PATH_A_IMPLEMENT_ARTIFACT_FIRST.
- Motivo: Artifact Server é a base transversal para anexos, outputs, downloads e storage privado; Chat Bridge e Designer dependem dele, e RAG also benefits from the storage boundary. Resolving secure storage, metadata, signed URLs, and limits first reduces coupling and avoids premature provider/UI work.
- Risco principal: storage/security mistakes are harder to unwind than adapter or UI wiring.
- Próxima fase: M1B_ARTIFACT_IMPLEMENTATION.

## 6. Dependências cruzadas
Veja o mapa em maps/cross-module-dependency-matrix.tsv. Summary: Chat Bridge and Designer both depend on Artifact; Designer also depends on Chat Bridge and RAG; RAG depends on Chat Bridge and backend-owned provider/vector-store boundaries.

## 7. Scorecard de decisão
Veja o mapa em maps/implementation-decision-scorecard.tsv. The recommended path is PATH_A_IMPLEMENT_ARTIFACT_FIRST because it has the highest combined value, dependency leverage, testability, and security profile.

## 8. Blockers de segurança
Veja o mapa em maps/security-blocker-register.tsv. Priorities are private storage, signed URL/HMAC, RBAC, audit logging, rate limiting, server-side provider keys, no direct frontend provider calls, tool/collection allowlists, job ownership, prompt validation, artifact ownership, and safe download headers.

## 9. Boundary NO-GO
Veja o mapa em maps/no-go-boundary.tsv. This phase does not change backend runtime, frontend runtime, Docker, auth providers, Vite proxying, or imported upstream services.

## 10. Roadmap de implementação
Veja o mapa em maps/next-implementation-roadmap.tsv. First real work should be M1B_ARTIFACT_IMPLEMENTATION, followed by M1C UAT, then mock adapters for Chat, RAG, and Designer.

## 11. Prompts gerados
- prompts/M1B_ARTIFACT_IMPLEMENTATION_PROMPT.md
- prompts/M2B_CHAT_BRIDGE_MOCK_ADAPTER_PROMPT.md
- prompts/M3B_RAG_MCP_MOCK_ADAPTER_PROMPT.md
- prompts/M4B_DESIGNER_MOCK_ADAPTER_PROMPT.md

## 12. O que não foi alterado
- backend code: not changed
- frontend code: not changed
- Docker: not changed
- imported ZIP/external code: not committed
- push: not executed

## 13. Validações
- This M5 consolidation is a docs-and-test decision phase.
- After file creation, validation gates are recorded in docs/audit/external-ens-unified-migration-m5-gates.log.

## 14. Limitações
- M1–M4 remain contract-first and do not imply runtime implementation yet.
- External services are intentionally kept out of the runtime boundary.
- Any future implementation must stay backend-owned and selective.

## 15. Decisão final
PATH_A_IMPLEMENT_ARTIFACT_FIRST is the first implementation to execute. Do not begin direct chat, RAG, or designer runtime work before the Artifact backend is real and verified.
