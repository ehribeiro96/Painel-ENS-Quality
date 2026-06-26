# ENS Unified Migration M4 — Designer API Module

## 1. Status
PARTIAL-GO

## 2. Objetivo
Definir o contrato seguro de Designer API Module para o Painel ENS-Quality/Apoema sem copiar o app inteiro, sem expor provider ao frontend e sem depender de geração real nesta fase.

## 3. Base M0/M1/M2/M3
- Commit M0: `af184b7`
- Commit M1: `e7841cb`, `eb71649`
- Commit M2: `5df11cd`, `44a94c1`
- Commit M3: `0cb9ae3`, `c13f449`
- Artifact contract status: `M1A_CONTRACT_ONLY`
- Chat bridge contract status: `M2A_CONTRACT_ONLY`
- RAG MCP contract status: `M3A_CONTRACT_ONLY`
- Runtime Apoema: porta `5175`, helper `scripts/dev-apoema-vite.sh`, proxy `http://[::1]:8080`

## 4. Fonte externa analisada
- DESIGNER_API_EXTERNAL_ROOT: `/tmp/ens-unificado-analysis/projeto-ens-unificado-main/apps/designer-api`
- Arquivos principais: `main.py`, `api/app.py`, `api/job_service.py`, `api/supabase_outputs.py`, `execution/select_template.py`, `execution/prompts.py`, `directives/banner_generation.md`, `directives/api_frontend_integration.md`, `directives/cloudflare_tunnel.md`, `tests/test_integration_mock.py`, `tests/test_template_payloads_consistency.py`
- Endpoints encontrados: GET /health, POST /banners, POST /banners/json, GET /templates, GET /banners/form-options, GET /banners/{job_id}, GET /banners/{job_id}/download, GET /banners/metrics/enxoval, POST /banners/{job_id}/items/{item_id}/adjust, POST /banners/{job_id}/items/{item_id}/refresh-url
- Templates/opções encontradas: canais=01_feed_instagram, 02_story_instagram, 03_banner_interno_desktop, 04_banner_interno_mobile, 05_AIDA_whatsapp, 05_whatsapp, 08_topo_email; kvs=graduacao, imersoes, institucional, pos, qualificacoes, tudo-sobre-seguros; template contexts=29; planner payloads presentes em parte do catálogo

## 5. Decisão da fase
- Fase escolhida: `M4A_CONTRACT_ONLY`
- Justificativa: M1, M2 e M3 permanecem contract-only; o Designer externo depende de provider keys, output storage e upload/download policies; a implementação segura precisa de Artifact M1 real e de um adapter backend-owned para chat/RAG antes de qualquer geração live.

## 6. Endpoints externos
Os endpoints externos principais são os listados acima. O external app também monta `/files` para outputs locais e publica docs/openapi padrão do FastAPI, mas isso não vira contrato alvo direto.

## 7. Jobs externos
Estados observados: pending, running, done, partial_done, failed.

## 8. Templates e opções
- Templates por canal/KV derivados de `templates_library/{canal}/{kv}/`
- Opções visíveis: `modo_geracao`, `canal`, `kv`, `box2`, `persona_image`, `x-user-id`
- Alguns templates possuem `planner_payloads`; outros apenas `template_context.json`
- Há discrepâncias de `template_id` em algumas pastas, então o target deve tratar o catálogo como server-owned e validar a origem explicitamente

## 9. Contrato alvo
Ver `maps/designer-api-target-contract.tsv`.

## 10. Job model/status
Ver `contracts/designer-job-contract.md` e `maps/designer-api-job-map.tsv`.

## 11. Integração com Artifact M1
Ver `contracts/designer-output-artifact-contract.md` e `maps/designer-api-artifact-dependencies.tsv`.

## 12. Integração com Chat Bridge M2/RAG M3
Ver `maps/designer-api-chat-rag-dependencies.tsv` e a contract docs correspondentes.

## 13. Segurança: auth/RBAC/audit/rate limit
Os controles obrigatórios incluem AUTH_REQUIRED, RBAC_REQUIRED, AUDIT_LOG_REQUIRED, RATE_LIMIT_REQUIRED, JOB_OWNERSHIP_CHECK e redaction/timeouts. O estado atual externo é parcialmente coberto, mas não suficiente para um target live seguro.

## 14. Provider isolation
Ver `contracts/designer-provider-isolation-contract.md`. Provider e model must remain backend-owned.

## 15. Prompt safety e cost control
O fluxo externo já mostra retries e toggles de planner/executor, mas falta política explícita de quota, sanitização de saída e gates de conteúdo.

## 16. O que foi implementado
- inventário da fonte externa
- mapas de endpoints/jobs/templates/env/security/dependencies
- documentos de contrato backend-owned
- teste estático do contrato

## 17. O que NÃO foi implementado
- backend designer router/adapters
- frontend Apoema changes
- Docker/Compose changes
- provider real Gemini/Imagen integration
- copy do app externo para o runtime atual

## 18. Validações
- `git diff --check`: PASS
- `PYTHONPATH=backend .venv/bin/python -m pytest`: PASS (278 passed, 22 skipped)
- `.venv/bin/python -m ruff check backend tests scripts`: PASS
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`: PASS
- `cd frontend/itam-platform && PATH="/home/estevaoqualityadm/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build`: PASS
- secret scan on docs/test artifacts: PASS (no matches)

## 19. Limitações
- O export externo inclui muita superfície de experimento e documentação; apenas o contrato de Designer API foi mapeado para a migração
- Output público local (`/files`) não é aceitável para o target
- Download real depende de Artifact M1 implementado

## 20. Próxima fase recomendada
`M5_MIGRATION_CONSOLIDATION_DECISION`
