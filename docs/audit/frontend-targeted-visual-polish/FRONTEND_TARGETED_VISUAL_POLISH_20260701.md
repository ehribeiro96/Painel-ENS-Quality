# FRONTEND_TARGETED_VISUAL_POLISH_20260701

## Status
GO.

## Escopo
- Correção visual direcionada após o QA final retornar PARTIAL-GO.
- Sem mudança de backend, contratos ou features.
- Polimento aplicado em roteamento, chat, login e tipografia de detalhe.

## O que foi ajustado
- Removido o par de rotas sem wildcard em `App.tsx` para eliminar o warning de React Router em `/apoema` e `/apoema-preview`.
- Ajustado o cabeçalho do chat para manter “Conversas” íntegro em vez de quebrar em duas linhas.
- Compactado o login para reduzir o espaço vazio vertical em desktop e mobile.
- Reforçado o wrapping seguro do título do detalhe de artefato.

## O que foi verificado
- Artifacts, Chat, RAG, Designer, Preview e Login renderizam nas viewports desktop e mobile.
- O sidebar mobile permanece funcional e navegável.
- O título do detalhe do artefato não apresenta mais sobreposição visual aparente.
- O warning de roteamento não reapareceu nas capturas de smoke reduzido.

## Evidências
- [visual-regression-smoke.tsv](./maps/visual-regression-smoke.tsv)
- [router-warning-check.tsv](./maps/router-warning-check.tsv)
- [polish-finding-closure.tsv](./maps/polish-finding-closure.tsv)
- [visual smoke logs](./raw/visual-polish-console-network.log)
- [login captures](./screenshots/desktop-1920/desktop-1920__login-before-auth__above.png)
- [chat capture](./screenshots/desktop-1920/desktop__chat__above.png)
- [artifact detail capture](./screenshots/desktop-1920/desktop__artifact-detail__above.png)

## Segurança
- Nenhum secret, cookie, token, storage state, path interno ou provider key apareceu nas capturas ou logs revisados.
- O único 401 observado no smoke foi do endpoint de refresh de autenticação ao abrir a tela de login, e não expôs credenciais.

## Gates
- `git diff --check`: pass
- `pytest -s -q`: pass
- `ruff`: pass
- `compileall`: pass
- `frontend build`: pass
- `docker compose config --services`: pass

## Decisão
GO. Os achados P2/P3 confirmados foram corrigidos ou validados como não bloqueadores, e a interface segue estável para operação normal.
