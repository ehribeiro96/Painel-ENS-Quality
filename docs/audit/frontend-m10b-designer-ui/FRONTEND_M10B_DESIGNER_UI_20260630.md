# FRONTEND M10B Designer UI

## Escopo

Implementação da UI Apoema para Designer API mock-determinística, usando somente o backend `/api/v1/designer/*`.

## Arquivos alterados

- `frontend/itam-platform/src/apoema/lib/apoemaDesignerApi.ts`
- `frontend/itam-platform/src/apoema/pages/DesignerPage.tsx`
- `frontend/itam-platform/src/apoema/pages/DesignerJobPage.tsx`
- `frontend/itam-platform/src/apoema/components/DesignerTemplateSelector.tsx`
- `frontend/itam-platform/src/apoema/components/DesignerBannerForm.tsx`
- `frontend/itam-platform/src/apoema/components/DesignerJobStatus.tsx`
- `frontend/itam-platform/src/apoema/components/DesignerJobItems.tsx`
- `frontend/itam-platform/src/apoema/types.ts`
- `frontend/itam-platform/src/apoema/ApoemaApp.tsx`
- `frontend/itam-platform/src/apoema/styles/apoema.css`
- `tests/test_apoema_designer_ui_contract.py`

## Endpoints consumidos

- `GET /api/v1/designer/health`
- `GET /api/v1/designer/templates`
- `GET /api/v1/designer/form-options`
- `POST /api/v1/designer/banners/json`
- `GET /api/v1/designer/jobs/{job_id}`
- `POST /api/v1/designer/jobs/{job_id}/items/{item_id}/adjust`
- `POST /api/v1/designer/jobs/{job_id}/items/{item_id}/refresh-url`
- `POST /api/v1/designer/jobs/{job_id}/cancel`

## Templates e opções consumidas

- Templates/canais: `01_feed_instagram`, `02_story_instagram`, `03_banner_interno_desktop`, `04_banner_interno_mobile`, `05_AIDA_whatsapp`, `05_whatsapp`, `08_topo_email`
- KVs: `graduacao`, `imersoes`, `institucional`, `pos`, `qualificacoes`, `tudo-sobre-seguros`
- Modos: `peca_unica`, `enxoval`

## Gaps fechados

- Rotas Apoema para `Designer` e `DesignerJob`
- Client API centralizada em `/api/v1/designer/*`
- Criação de job via `/banners/json`
- Exibição de health, templates e form-options
- Exibição de job e itens
- Ações permitidas: `adjust`, `refresh-url`, `cancel`
- Mensagem honesta de modo mock/determinístico
- Teste de contrato estático para UI Designer

## Gaps não implementados

- Provider real
- `download-url`
- Integração com Artifact
- Integração com Chat
- Integração com RAG

## Segurança

- Sem provider direto no frontend
- Sem provider key exposta
- Sem path interno ou storage path exposto
- Sem download token sensível renderizado
- Sem fallback que mascare `401`, `403` ou `429`

## Gates

- `git diff --check`
- `pytest -s -q`
- `ruff check backend tests scripts`
- `compileall -q backend/app backend/alembic tests scripts`
- `npm run build`
- `docker compose config --services`

## Push

Não executado.
