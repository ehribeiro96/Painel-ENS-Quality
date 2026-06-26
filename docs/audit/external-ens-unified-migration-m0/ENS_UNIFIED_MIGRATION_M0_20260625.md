# ENS Unified Migration M0 — Plano Mestre de Migração para Apoema

## 1. Status
GO/PARTIAL-GO/NO-GO: GO

## 2. Objetivo
Planejar a migração correta do projeto ENS Unificado para o Painel ENS-Quality/Apoema sem alterar runtime.

## 3. Fonte externa
- Caminho Windows: C:\Users\estevao.quality\Desktop\projeto-ens-unificado-main.zip
- Caminho WSL: /mnt/c/Users/estevao.quality/Desktop/projeto-ens-unificado-main.zip
- Extração temporária: /tmp/ens-unificado-analysis
- ZIP commitado: não

## 4. Sumário executivo
- Migração direta: não
- Módulos aprovados: services/artifact-server, services/chat-bridge, services/rag-mcp, apps/designer-api
- Módulos bloqueados: apps/chat-web, services/hermes-runtime, services/hermes-runtime/vendor/hermes-agent
- Riscos críticos: R-001, R-002, R-004
- Ordem recomendada: M1 Artifact Server Contract → M2 Chat Bridge Hermes Adapter → M3 RAG MCP External Service → M4 Designer API Module → M5 Apoema UI Entrypoints → M6 Authenticated UAT → M7 Pre-push Checklist

## 5. Estado do projeto atual
- O repositório local já está em Apoema como frente principal.
- Existem muitos untracked preservados fora da boundary M0.
- Não houve mudança de runtime nesta fase.

## 6. Runtime operacional
- Porta Apoema: 5175
- Helper: scripts/dev-apoema-vite.sh
- Proxy: http://[::1]:8080
- URL Windows: http://127.0.0.1:5175/apoema

## 7. Inventário do projeto externo
- Total de arquivos extraídos: 5812
- Total de diretórios observados: 279
- Top-level: apps, services, docs, infra, scripts, docker-compose.yml
- Módulos centrais identificados: chat-web, designer-api, artifact-server, chat-bridge, rag-mcp, hermes-runtime, vendor/hermes-agent

## 8. Módulos aproveitáveis
- services/artifact-server: contrato primeiro
- services/chat-bridge: adapter após contrato
- services/rag-mcp: service/adapter externo
- apps/designer-api: módulo opcional de backend

## 9. Módulos proibidos
- apps/chat-web: shell legado/conflictivo com Apoema
- services/hermes-runtime: runtime bundle de orquestração, não alvo de migração direta
- services/hermes-runtime/vendor/hermes-agent/**: subtree vendorizado de alto risco

## 10. Segurança e segredos
- Segredos reais encontrados: não
- Evidências sensíveis foram redigidas em qualquer snapshot textual.
- Não há autorização para levar tokens, cookies, storageState ou .env reais para o repositório.

## 11. Contratos de API candidatos
- artifact-server: /health, /v1/artifacts, /v1/artifacts/:id, /v1/artifacts/:id/access-link, /v1/artifacts/:id/content, DELETE /v1/artifacts/:id
- chat-bridge: /health, /api/chat/session/delete, /api/chat/runs, /api/chat/stream, /api/chat/runs/:id/events
- rag-mcp: /health, /mcp
- designer-api: /health, /banners, /banners/{job_id}, /banners/form-options, /banners/metrics/enxoval, /files

## 12. Mapa de variáveis de ambiente
- O mapa foi extraído e classificado em docs/audit/external-ens-unified-migration-m0/maps/env-variable-map.tsv.
- Classificações usadas: PUBLIC_FRONTEND_ALLOWED, SERVER_ONLY_SECRET, LOCAL_DEV_ONLY, REMOVE_OR_SANITIZE, UNKNOWN_REVIEW_REQUIRED.

## 13. Decisão por módulo
- artifact-server: APPROVE_FOR_CONTRACT_MIGRATION
- chat-bridge: APPROVE_FOR_ADAPTER_DESIGN
- rag-mcp: APPROVE_FOR_ADAPTER_DESIGN
- designer-api: APPROVE_FOR_ADAPTER_DESIGN
- chat-web: DO_NOT_MIGRATE
- hermes-runtime: DO_NOT_MIGRATE
- vendor/hermes-agent: QUARANTINE_SECURITY_REVIEW

## 14. Roadmap M1-M7
- M1 Artifact Server Contract
- M2 Chat Bridge Hermes Adapter
- M3 RAG MCP External Service
- M4 Designer API Module
- M5 Apoema UI Entrypoints
- M6 Authenticated UAT
- M7 Pre-push Checklist

## 15. Prompts gerados para próximas fases
- docs/audit/external-ens-unified-migration-m0/prompts/M1_ARTIFACT_SERVER_CONTRACT_PROMPT.md
- docs/audit/external-ens-unified-migration-m0/prompts/M2_CHAT_BRIDGE_HERMES_PROMPT.md
- docs/audit/external-ens-unified-migration-m0/prompts/M3_RAG_MCP_PROMPT.md
- docs/audit/external-ens-unified-migration-m0/prompts/M4_DESIGNER_API_PROMPT.md

## 16. O que não foi alterado
- Backend runtime: não alterado
- Frontend runtime: não alterado
- Docker Compose: não alterado
- ZIP externo: não commitado
- Push: não executado

## 17. Validações
- ZIP validado em /mnt/c/Users/estevao.quality/Desktop/projeto-ens-unificado-main.zip
- Extração temporária apenas em /tmp/ens-unificado-analysis
- grep/scan de segredos executado sobre o material externo
- diffs do repositório locais ainda não staged fora da boundary M0

## 18. Limitações
- O projeto externo é grande; a análise priorizou manifests, entrypoints e contratos centrais.
- Vendor/hermes-agent foi tratado como subtree quarantined para evitar migração insegura.
- Qualquer evolução de runtime deve ser tratada nas fases M1-M7, não em M0.

## 19. Próxima ação recomendada
- Iniciar M1_ARTIFACT_SERVER_CONTRACT com stage seletivo e testes de contrato backend-only.
