# ENS Unified Migration M1C — Artifact UAT

## 1. Status
PARTIAL-GO

## 2. Objetivo
Validar o runtime real do backend para artifacts após a M1B, confirmando rota carregada, UAT autenticado local, upload/download/delete e rejeições de segurança sem alterar frontend ou migrations.

## 3. Base M1B
- M1B foi concluída com GO.
- Endpoints implementados no contrato M1B: POST/GET/GET by id/download-url/download signed/DELETE em /api/v1/artifacts.
- Storage privado e metadata sem path interno estavam no contrato M1B.
- Smoke anterior em localhost:8080 e [::1]:8080 retornou 404 not_found sem validar o novo código.

## 4. Runtime analisado
- Container live: painel-ens-quality-app-1
- Health readiness: 200 OK
- Runtime live aceitou login autenticado e UAT completo de artifacts.
- Auth gate validado no runtime live: GET /api/v1/artifacts sem token responde 401 Unauthorized (detail=missing_token), não 404 not_found.

## 5. Rotas carregadas no OpenAPI
- /api/v1/artifacts
- /api/v1/artifacts/{artifact_id}
- /api/v1/artifacts/{artifact_id}/download-url
- /api/v1/artifacts/download/{signed_token}

## 6. Rebuild/restart
- Sim, executado de forma controlada com docker compose up -d --build app.
- O container permaneceu healthy após a operação.

## 7. Auth gate
- Sem token: GET /api/v1/artifacts retornou 401 Unauthorized (detail=missing_token).
- Com token admin local: login e chamadas protegidas funcionaram.

## 8. Upload permitido
- OK em runtime real.
- Upload de allowed.txt retornou 201.

## 9. Metadata
- OK em runtime real.
- Metadata retornou campos seguros: id, owner_user_id, filename, content_type, size_bytes, sha256, created_at, updated_at, download_count, deleted_at, deleted_by.
- Nenhum path interno foi exposto.

## 10. Download URL
- OK em runtime real.
- download-url retornou objeto com artifact_id, expires_at e url.

## 11. Download assinado
- OK em runtime real.
- Download assinado retornou 200 e o corpo conferiu com o arquivo pequeno permitido.
- Content-Disposition seguro foi emitido.

## 12. Rejeições de segurança
- Extensão proibida: bloqueada com 400 invalid_extension.
- MIME proibido: bloqueado com 400 invalid_mime_type.
- Path traversal: bloqueado com 400 invalid_filename.

## 13. Delete
- OK em runtime real.
- DELETE retornou 200 com deleted_at.

## 14. Storage privado
- Validado por contrato e runtime: manifest/privado separado, sem path interno exposto nos DTOs.
- .gitignore protege data/artifacts/private/ e data/artifacts/metadata.json.
- Nenhum blob de artifact apareceu em git status do repositório.

## 15. O que não foi testado
- Criação de usuário UAT sintético novo não foi necessária.
- Não houve alteração de frontend.
- Não houve alteração de migrations.
- Não foi criada correção de código, pois o fluxo autenticado já funcionou em runtime.

## 16. Riscos restantes
- O auth gate sem token agora está alinhado ao contrato (401/403) e não bloqueia mais a conclusão da fase.
- O runtime depende de validação operacional contínua para manter o contrato alinhado em futuros deploys.

## 17. Próxima fase recomendada
- M2B_CHAT_BRIDGE_MOCK_ADAPTER

## Evidência resumida
- Runtime route presente no OpenAPI: sim.
- UAT autenticado executado: sim.
- Upload/download/delete e rejeições de segurança: sim.
- Auth gate sem token: não conforme ao contrato.
