# PRODUCT-H1 — Executive Summary

## Status

GO documental.

A boundary PRODUCT-H1 cumpriu seu objetivo de planejamento: avaliou maturidade funcional, definiu MVP operacional, priorizou evolução por valor, criou backlog em boundaries pequenas, registrou cenários UAT, consolidou do-not-touch e atualizou a próxima decisão de boundary.

Ressalva: o repositório continua com muitos untracked antigos já conhecidos. O stage inicial estava vazio e o trabalho desta boundary não stageou nada.

## Decisão principal

O Painel ENS-Quality está pronto para sair de higiene/auditoria e entrar em validação funcional real, mas a próxima ação não deve ser implementação direta. A decisão correta é executar UAT ponta-a-ponta com dados sintéticos para provar o fluxo crítico:

Ativo → Movimentação → Macro → Histórico → Copiar macro → Auditoria.

## Próxima boundary recomendada

`UAT-H1 — end-to-end operational scenario validation`

Motivo:
- O fluxo existe tecnicamente, mas precisa ser provado na rotina N2.
- Há indício de lacuna UX no pós-movimentação: o modal pode fechar após `onMoved()` antes do operador usar a macro exibida.
- UAT separa bugs reais de impressões e evita mexer no fluxo sensível sem evidência.

## Top 5 prioridades

1. Executar UAT-H1 com 10 cenários sintéticos.
2. Validar comportamento pós-movimentação e visibilidade da macro oficial.
3. Confirmar rastreabilidade histórico/auditoria para movimento, geração e cópia.
4. Endurecer legibilidade operacional de ativo/movimentação para N2.
5. Preservar áreas validadas: imports, Ollama LAN, CSP legado, Docker volumes, migrations e CI manual-only.

## Top 5 riscos

1. Macro pós-movimentação ficar invisível por fechamento do modal após `onMoved()`.
2. Histórico mostrar IDs truncados em vez de informação útil para o operador.
3. Auditoria sem filtros dificultar prova diária de rastreabilidade.
4. Evolução funcional tocar ImportService, IA/Ollama ou legacy sem boundary própria.
5. Worktree com untracked antigos induzir stage/commit acidental fora de escopo.

## MVP proposto

MVP Operacional N2:
- Criar/localizar ativo.
- Importar ativo com staging e apply seguro.
- Movimentar ativo com confirmação explícita e justificativa.
- Gerar macro ITIL oficial somente após movimento salvo.
- Copiar macro persistida e marcar `copied`.
- Ver histórico do ativo.
- Ver auditoria do ciclo.
- Usar AI Chat apenas como apoio textual, sem alteração autônoma de dados.

## O que não mexer

- Provider `ollama-lan`.
- Baseline `qwen3:1.7b-64k`.
- Sanitização `<think>`.
- ImportService validado.
- CSP legado.
- Migrations estáveis.
- Docker volumes.
- Workflow Docker manual-only.
- Assets runtime já commitados.
- Pytest markers recentes.
- Untracked sensíveis/legados não decididos.
- Auth/RBAC sem plano.
- Fluxo MoveAssetDialog sem UAT/feature boundary.

## Sequência recomendada

1. `UAT-H1 — end-to-end operational scenario validation`
2. `MOV-H1 — movement creation and validation hardening`, se UAT confirmar lacunas de movimentação.
3. `MACRO-H1 — ITIL macro generation polish`, se UAT confirmar lacunas de macro/cópia.
4. `HISTORY-H1 — history and audit traceability`.
5. `ASSET-H1 — asset detail and lifecycle hardening`.
6. `AI-H1 — AI assisted macro explanation and suggestion`.
7. `REPORT-H1 — operational dashboard and export`.
8. `UX-H1 — route-level usability polish` orientado por achados do UAT.
9. `RELEASE-H1 — production readiness checklist`.
