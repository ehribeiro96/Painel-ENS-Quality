# MANUAL-VISUAL-REVIEW-H1 — Checklist de Revisão Visual Manual

## Status

Pronto para revisão humana final.

## Objetivo

Validar visualmente o estado final autenticado do sistema antes da próxima boundary de release.

## Pacote temporário

- `/tmp/manual_visual_review_h1/index.html`
- `/tmp/manual_visual_review_h1/README.md`
- `/tmp/manual_visual_review_h1/screenshots/desktop/before`
- `/tmp/manual_visual_review_h1/screenshots/desktop/after`
- `/tmp/manual_visual_review_h1/screenshots/mobile/before`
- `/tmp/manual_visual_review_h1/screenshots/mobile/after`
- `/tmp/manual_visual_review_h1/logs/summary_before.json`
- `/tmp/manual_visual_review_h1/logs/summary_after.json`

## Rotas capturadas

- `/login`
- `/`
- `/assets`
- `/audit-logs`
- `/imports`
- `/settings`
- `/macros`
- `/users`
- `/signatures`
- `/stock`
- `/ai-chat`
- `/__not_found__`
- `/assets/<id>` no desktop

## Critérios de revisão

- sem overflow horizontal;
- shell lateral legível em desktop e mobile;
- cards e tabelas sem sobreposição;
- macros visíveis após movimentação;
- copy flow preservado onde aplicável;
- rota `404` sem quebra visual;
- página de detalhe de ativo sem regressão visual aparente;
- sem segredo em screenshots, logs ou docs.

## O que não foi alterado

- backend;
- migrations;
- package files;
- API client;
- auth;
- permissões;
- movimento/apply;
- base44 runtime;
- qualquer arquivo fonte fora de docs.

## Próxima ação humana

Abrir `/tmp/manual_visual_review_h1/index.html` e aprovar ou rejeitar a revisão visual.
