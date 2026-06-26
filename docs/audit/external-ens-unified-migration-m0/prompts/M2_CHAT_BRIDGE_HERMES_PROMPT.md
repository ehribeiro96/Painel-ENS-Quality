# M2 — Chat Bridge Hermes Adapter

Objetivo
- Evoluir o chat-bridge como adaptador do Hermes com base no contrato já estabilizado do artifact-server.

Contexto
- A UI do Apoema chama o backend atual; o backend decide auth, RBAC, rate limit e auditoria.
- O chat bridge não deve expor provider direto para o frontend.
- Dependências de artifact-link rewriting e SSE/stream devem ser tratadas como contrato server-side.

Boundary
- Permitido: docs do adapter, mapeamento de DTOs, testes de contrato, documentação de fluxo de sessão/run/stream.
- Proibido: copiar frontend legado, mudar auth atual, mudar backend runtime fora do adapter, tocar Docker Compose sem necessidade.

Arquivos permitidos
- docs/audit/external-ens-unified-migration-m0/**
- futuras alterações em serviços/adapter específicas do M2 apenas após aprovação.

Arquivos proibidos
- apps/chat-web/src/**
- frontend/itam-platform/src/**
- backend/app/** fora do adapter aprovado
- .env*
- storageState/cookies/tokens
- vendor/hermes-agent/**

Validações
- Cobrir /health, /api/chat/session/delete, /api/chat/runs, /api/chat/stream, /api/chat/runs/:id/events.
- Confirmar verifyUser() / RBAC server-side.
- Confirmar que artifacts são convertidos via link/access-link no backend.

Segurança
- Nada de credenciais no frontend.
- Nada de secret em logs, docs ou exemplos.
- Mantém auditoria/histórico para qualquer mutação.

Stage seletivo
- Stage apenas arquivos do adapter M2.
- Se algum teste for criado, ele deve cobrir o contrato e a segurança do fluxo.

Commits seletivos
- Commit único por unidade de mudança pequena.
- Nunca incluir arquivos alheios ao adapter.

Sem push
- Não fazer push.
- Não fazer merge automático.
- Não fazer rebase automático.
