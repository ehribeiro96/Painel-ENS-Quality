# ENS Unified Migration M4B — Designer Mock Adapter

## 1. Status
GO

## 2. Objetivo
Implementar um adapter backend mock/determinístico para Designer API no Painel ENS-Quality/Apoema, sem provider real, sem geração real de imagem, sem blob/output real, sem frontend novo e sem migrations.

## 3. Base M1C / M2B / M3B
- M1C Artifact UAT: GO
- M2B Chat Bridge Mock Adapter: GO
- M3B RAG MCP Mock Adapter: GO
- Esta fase respeita os contratos anteriores e não altera o frontend nem o armazenamento de artifacts.

## 4. O que foi implementado
- Router backend-owned para `/api/v1/designer`
- DTOs explícitos para health, templates, form-options, jobs e erros
- Serviço mock determinístico com store in-memory controlado
- Allowlist server-side para templates, canais, KVs e modo de geração
- Criação de job mock determinístico via JSON
- Consulta de job mock determinística
- Ajuste de item mock determinístico
- Refresh-url mock determinístico
- Cancelamento mock determinístico
- Endpoints bloqueados para multipart/banner e download-url real
- Testes de contrato e segurança
- Documentação M4B

## 5. Endpoints criados
- GET /api/v1/designer/health
- GET /api/v1/designer/templates
- GET /api/v1/designer/form-options
- POST /api/v1/designer/banners/json
- GET /api/v1/designer/jobs/{job_id}
- POST /api/v1/designer/jobs/{job_id}/items/{item_id}/adjust
- POST /api/v1/designer/jobs/{job_id}/items/{item_id}/refresh-url
- POST /api/v1/designer/jobs/{job_id}/cancel
- POST /api/v1/designer/banners (bloqueado nesta fase)
- GET /api/v1/designer/jobs/{job_id}/download-url (bloqueado nesta fase)

## 6. Templates allowlist
- 01_feed_instagram
- 02_story_instagram
- 03_banner_interno_desktop
- 04_banner_interno_mobile
- 05_AIDA_whatsapp
- 05_whatsapp
- 08_topo_email

## 7. Form options allowlist
- canais: os mesmos 7 templates allowlisted
- kvs: graduacao, imersoes, institucional, pos, qualificacoes, tudo-sobre-seguros
- modos: peca_unica, enxoval
- box2: opcional
- persona_image: opcional
- limites server-side: prompt/copy até 2000 caracteres; até 12 itens por job

## 8. Mock determinístico
- job_id e item_id são gerados no backend
- o mesmo payload do mesmo usuário retorna o mesmo job enquanto o store in-memory permanece ativo
- status padrão de job/item: completed
- refresh/adjust/cancel atualizam apenas metadados mock
- nenhum provider real é chamado
- nenhum blob real é gravado
- nenhum arquivo de download real é gerado

## 9. Job model
- job_id
- owner_user_id
- status
- created_at
- updated_at
- template_id
- canal
- kv
- modo_geracao
- box2
- persona_image_present
- prompt_preview
- copy_preview
- progress
- items[]
- summary
- error redigido

## 10. Auth / RBAC / rate / audit
- AUTH_REQUIRED: sim, preservado por get_current_user
- RBAC_OR_ROLE_GATE: sim, aplicado nas rotas de escrita
- 401 missing_token: sim, preservado pelo auth gate atual
- RATE_LIMIT_IF_PATTERN_EXISTS: sim, herdado do middleware global da API
- AUDIT_LOG_IF_PATTERN_EXISTS: parcialmente atendido via histórico/event log in-memory do mock; não há persistência DB nesta fase
- JOB_OWNERSHIP_CHECK: sim, o job só é mutável pelo dono ou admin
- ERROR_REDACTION: sim, códigos/sumarização sem payload de provider

## 11. O que não foi implementado
- geração real de imagem
- provider real Gemini/Imagen/Vertex/OpenAI/Ollama
- download real baseado em artifact output
- frontend novo
- migrations
- Docker/Compose
- gravação de blob/output real

## 12. Riscos restantes
- store é process-local e não persiste entre reinícios
- download-url real depende de Artifact M1
- auditoria persistida em banco ainda não foi promovida para este adapter mock

## 13. Próxima fase recomendada
M6_AUTHENTICATED_E2E_AND_UI_GATE
