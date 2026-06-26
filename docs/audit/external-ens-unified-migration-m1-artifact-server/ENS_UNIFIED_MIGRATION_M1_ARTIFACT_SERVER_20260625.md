# ENS Unified Migration M1 — Artifact Server Contract

## 1. Status
PARTIAL-GO

## 2. Objetivo
Definir o contrato seguro de Artifact Server para o Painel ENS-Quality/Apoema sem copiar o serviço inteiro e sem expor storage diretamente ao frontend.

## 3. Base M0
- Commit M0: `af184b7`
- Módulo externo: `services/artifact-server`
- Runtime Apoema: porta `5175`, helper `scripts/dev-apoema-vite.sh`, proxy `http://[::1]:8080`

## 4. Fonte externa analisada
- ARTIFACT_EXTERNAL_ROOT: `/tmp/ens-unificado-analysis/projeto-ens-unificado-main/services/artifact-server`
- Arquivos principais: `src/server.js`, `test/artifact-server.test.js`, `package.json`, `Dockerfile`, `docker-entrypoint.sh`, `.dockerignore`
- Endpoints encontrados: `/health`, `/v1/artifacts`, `/v1/artifacts/:id`, `/v1/artifacts/:id/access-link`, `/v1/artifacts/:id/content`, `DELETE /v1/artifacts/:id`

## 5. Decisão da fase
- M1A_CONTRACT_ONLY
- Justificativa: o contrato externo é claro o suficiente para documentar, mas a implementação segura no backend atual ainda exigiria decisões adicionais de storage, RBAC fino, audit trail e política de retenção. Nesta fase não houve aprovação para migration/database work.

## 6. Contrato externo
O serviço externo é um HTTP server Node com storage privado em `data/`, metadata separada de blob, upload autenticado por bearer interno, signed access-link e download por token/HMAC.

## 7. Contrato alvo
O contrato alvo do Painel ENS-Quality é backend-owned, DTO-based e não expõe storage ao frontend.

Endpoints alvo:
- `POST /api/v1/artifacts`
- `GET /api/v1/artifacts`
- `GET /api/v1/artifacts/{artifact_id}`
- `GET /api/v1/artifacts/{artifact_id}/download-url`
- `GET /api/v1/artifacts/download/{signed_token}`
- `DELETE /api/v1/artifacts/{artifact_id}`

## 8. Segurança de upload
- upload autenticado
- size limit configurável
- safe filename sanitization
- server-generated IDs
- allowlist de MIME/extensão reservada para implementação futura

## 9. Armazenamento privado
A política alvo define armazenamento local privado sob `data/artifacts/private/` ou equivalente backend controlado, com metadata e blob separados.

## 10. Links assinados
Signed URLs devem ser HMAC-SHA256, curtas, com expiração explícita e verificação em tempo constante.

## 11. RBAC/Auth/Audit
Auth: sim no contrato alvo. RBAC: sim para upload/delete. Audit: sim para upload, mint de link, download e delete.

## 12. Rate limit
Deve existir para upload e geração de link assinado; o serviço externo não mostrou rate limit próprio.

## 13. O que foi implementado
- documentação de contrato
- mapa de endpoints
- mapa de envs
- controles de segurança
- testes estáticos de contrato

## 14. O que NÃO foi implementado
- backend artifacts router
- storage service no backend atual
- frontend Apoema
- integração Chat Bridge
- Docker/Compose changes

## 15. Validações
A validação principal desta fase é estática e documental, com teste dedicado ao contrato de artefatos.

## 16. Limitações
- não houve importação direta do serviço externo
- não houve criação de UI
- não houve alteração ampla de auth/RBAC
- não houve migration de banco

## 17. Próxima fase recomendada
`M2_CHAT_BRIDGE_HERMES_ADAPTER`
