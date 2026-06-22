# MANUAL-VISUAL-REVIEW-H1 — Screenshot Index

## Status

Índice preparado para leitura humana; as imagens ficam fora do repositório em `/tmp/manual_visual_review_h1`.

## Estrutura do pacote

- `index.html`: galeria navegável com `before` e `after`.
- `README.md`: instruções rápidas.
- `screenshots/desktop/before` e `screenshots/desktop/after`.
- `screenshots/mobile/before` e `screenshots/mobile/after`.
- `logs/summary_before.json` e `logs/summary_after.json`.
- `dom/README.md`: marcador de diretório reservado.

## Cobertura resumida

| Rota | Desktop | Mobile | Observação |
| --- | --- | --- | --- |
| `/login` | before/after | before/after | captura da tela de login |
| `/` | before/after | before/after | home autenticada |
| `/assets` | before/after | before/after | listagem principal |
| `/audit-logs` | before/after | before/after | histórico/auditoria |
| `/imports` | before/after | before/after | fluxo de importação |
| `/settings` | before/after | before/after | configurações |
| `/macros` | before/after | before/after | macro autocomplete e overlay |
| `/users` | before/after | before/after | usuários |
| `/signatures` | before/after | before/after | assinaturas |
| `/stock` | before/after | before/after | estoque |
| `/ai-chat` | before/after | before/after | IA Chat |
| `/__not_found__` | before/after | before/after | 404 de fallback |
| `/assets/<id>` | before/after | desktop somente | detalhe do ativo; mobile foi marcado como `skipped_no_visible_asset` |

## Regra de leitura

- Use a galeria em `index.html` para abrir cada screenshot.
- Priorize o estado `after`.
- Use `before` apenas para comparação visual.

## Limites

- Nenhum cookie, token, storage state ou credencial foi versionado.
- Nenhum arquivo fonte foi alterado para montar este índice.
