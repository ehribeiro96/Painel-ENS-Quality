# M3 — RAG MCP External Service

Objetivo
- Consolidar o rag-mcp como serviço externo/adapter independente, sem acoplar provider ou transporte diretamente ao frontend.

Contexto
- O serviço expõe /health e /mcp (POST) e funciona como MCP gateway para coleções ENS.
- A migração correta é service-first, não UI-first.

Boundary
- Permitido: docs, contrato do transporte MCP, mapeamento de config/env, testes de health e transport.
- Proibido: tocar frontend de Apoema, substituir auth existente, modificar Docker Compose fora do serviço, copiar vendor tree.

Arquivos permitidos
- docs/audit/external-ens-unified-migration-m0/**
- futuros arquivos do serviço M3, se aprovados.

Arquivos proibidos
- apps/chat-web/**
- frontend/itam-platform/src/**
- backend/app/** fora do adapter M3
- vendor/hermes-agent/**
- .env*
- tokens/keys/storageState

Validações
- Health check 200 JSON com ok=true.
- /mcp aceita POST e rejeita GET/DELETE com 405.
- Configuração de Supabase e transport sem expor segredo no cliente.

Segurança
- Credenciais somente em backend/runtime secret store.
- Sem provider direto para browser.
- Sem mutação sem preview/aprovação.

Stage seletivo
- Stage seletivo somente dos arquivos do serviço M3.
- Não incluir arquivos de outras fases.

Commits seletivos
- Commit pequeno por ajuste de contrato ou validação.
- Nunca usar git add .

Sem push
- Não fazer push.
- Não fazer push --force.
- Não fazer merge/rebase automáticos.
