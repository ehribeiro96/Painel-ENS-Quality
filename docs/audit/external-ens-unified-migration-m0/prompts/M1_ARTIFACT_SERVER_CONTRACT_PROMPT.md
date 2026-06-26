# M1 — Artifact Server Contract

Objetivo
- Estabilizar o contrato do artifact-server como primeira fronteira da migração ENS Unificado para Apoema.

Contexto
- Fonte externa: ZIP do ENS Unificado analisado somente em /tmp.
- Este passo não altera runtime do Apoema nem migra frontend legado.
- A prioridade é formalizar o contrato de upload, metadata, content delivery e access-link para consumo por adapters.

Boundary
- Permitido: docs do contrato, DTOs explícitos, testes de contrato, notas de mapeamento, validações.
- Proibido: alterar backend runtime atual, alterar frontend runtime atual, copiar código externo para o repositório, tocar Docker Compose, tocar auth/RBAC, tocar migrations.

Arquivos permitidos
- docs/audit/external-ens-unified-migration-m0/**
- arquivos de teste/contrato explicitamente criados para o plano M1, se forem necessários no futuro e só após aprovação.

Arquivos proibidos
- backend/**
- frontend/itam-platform/src/**
- frontend/itam-platform/vite.config.ts
- scripts/**
- docker-compose.yml
- package-lock.json
- migrations/**
- .env*
- qualquer arquivo dentro do ZIP externo

Validações
- Verificar que o contrato inclui: GET /health, POST /v1/artifacts, GET /v1/artifacts/:id, POST /v1/artifacts/:id/access-link, GET/HEAD /v1/artifacts/:id/content, DELETE /v1/artifacts/:id.
- Confirmar que respostas usam DTOs explícitos e não expõem modelo bruto.
- Confirmar que acessos sensíveis são backend-only.

Segurança
- Não colocar segredos em prompt, docs, testes ou exemplos.
- Não expor tokens, cookies, authorization headers, private keys ou storageState.
- Não permitir provider externo direto no frontend.

Stage seletivo
- Trabalhar somente na boundary de contrato do artifact server.
- Se houver necessidade futura de code changes, stage seletivo apenas dos arquivos do M1.

Commits seletivos
- Usar commit pequeno e focado em contrato, se e somente se houver mudança real.
- Nunca usar git add .

Sem push
- Não fazer push.
- Não fazer push --force.
- Não fazer push --force-with-lease.
