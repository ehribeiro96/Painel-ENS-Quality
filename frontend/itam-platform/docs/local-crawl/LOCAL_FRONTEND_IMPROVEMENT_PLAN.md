# Local Frontend Improvement Plan — HermesOps Sentinel

## Fase 1 — correções bloqueantes
Status: concluída

- Problema: frontend dev server 5173 usava `/api/v1` relativo e recebia 404.
  - Correção: Vite proxy para `http://127.0.0.1:8000`.
  - Arquivo: `frontend/itam-platform/vite.config.ts`
  - Resultado: login no 5173 agora autentica e carrega dados do backend local.

- Problema: AI Chat local retornava 404.
  - Correção: o backend local passou a habilitar `ai_chat` quando o ambiente é local.
  - Arquivo: `backend/app/core/config/settings.py`
  - Resultado: `/api/v1/ai-chat/*` responde com endpoints reais e não com 404.

## Fase 2 — UX de fluxos críticos
- Desafio: dashboards e listas dependem de pouca amostra local e exibem zero/empty states.
- Evidência: dashboard, stock e macros com contadores zerados.
- Arquivos prováveis: seeds/bootstrap de dados.
- Prioridade: P2.
- Critério de aceite: dashboard apresenta métricas mínimas e tabelas com amostra útil.

## Fase 3 — páginas fora do design system
- Desafio: portal legado precisa continuar visualmente separado do fluxo novo.
- Evidência: nav contém link para portal legado.
- Arquivos prováveis: páginas de assinaturas/legado.
- Prioridade: P3.
- Critério de aceite: rotas novas e legado têm affordances visuais distintas.

## Fase 4 — acessibilidade
- Desafio: manter labels/aria consistentes em filtros e busca global em todas as variantes responsivas.
- Evidência: auditado sem bloqueios, mas requer regressão contínua.
- Prioridade: P3.
- Critério de aceite: todos os inputs têm nome acessível verificável.

## Fase 5 — performance
- Desafio: bundle principal do frontend continua grande.
- Evidência: vite build output.
- Prioridade: P3.
- Critério de aceite: redução de bundle ou split por rota/feature.

## Fase 6 — refinamento visual
- Desafio: telas vazias podem parecer densas, mas sem quebra visual.
- Evidência: dashboard/imports/macros.
- Prioridade: P3.
- Critério de aceite: cards vazios usam hierarquia visual mais suave.
