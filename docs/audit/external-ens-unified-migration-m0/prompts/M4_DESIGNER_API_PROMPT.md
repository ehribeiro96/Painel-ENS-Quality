# M4 — Designer API Module

Objetivo
- Tratar o designer-api como módulo opcional de backend, com contrato explícito para jobs e arquivos, sem substituir o runtime atual.

Contexto
- O serviço tem /health, /banners, /banners/{job_id}, /banners/form-options, /banners/metrics/enxoval, /files e sub-recursos de ajuste/download.
- O fluxo precisa permanecer autenticado e auditable, com DTOs explícitos.

Boundary
- Permitido: docs do contrato, mapeamento de DTOs, validações de arquivo, documentação de job lifecycle.
- Proibido: migrar frontend legado, mexer no AuthProvider atual, alterar backend runtime fora do módulo aprovado, expor file mount publicamente sem política.

Arquivos permitidos
- docs/audit/external-ens-unified-migration-m0/**
- futuros arquivos do módulo M4 apenas após aprovação.

Arquivos proibidos
- apps/chat-web/**
- frontend/itam-platform/src/**
- backend/app/** fora do módulo aprovado
- .env*
- storageState/cookies/tokens
- vendor/hermes-agent/**

Validações
- Confirmar POST /banners e GET /banners/{job_id} com response models explícitos.
- Confirmar mount /files e download URLs só com política autenticada.
- Confirmar que output/job metadata não revela segredo.

Segurança
- Nunca mover API keys ou roles para frontend.
- Nunca copiar outputs gerados para o repo como artefato.
- Sempre revisar signed URLs e file access.

Stage seletivo
- Stage seletivo apenas para docs/contratos do módulo M4.
- Nada de alteracao cross-boundary.

Commits seletivos
- Commitar somente a unidade aprovada.
- Nunca usar git add .

Sem push
- Não fazer push.
- Não fazer push --force.
- Não fazer merge/rebase automáticos.
