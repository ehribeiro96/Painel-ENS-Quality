# M6 Authenticated E2E Rerun — 2026-06-26

## Status
GO

## Escopo
Fase `M6_AUTHENTICATED_E2E_RERUN` executada localmente, mantendo push bloqueado e sem alterar backend, frontend, Docker Compose, migrations, providers reais, MCP real, vector store real ou geração real de imagem.

## Push/remoto
- Branch: main.
- Divergência inicial observada: `0 151` em `origin/main...HEAD`.
- Push executado: não.
- Remote: `origin git@github.com:OWNER/REPO.git`.

## Histórico local e segredos
- Scanner redigido salvo em `history-rescan-redacted.json`.
- Total de achados heurísticos: 460.
- `jwt_like`: 0.
- `bearer_like`: 0.
- Classificação: sem JWT real e sem bearer real no intervalo `origin/main..HEAD`; achados restantes são falsos positivos documentais/código/binários versionados previamente, registrados apenas por hash de linha.

## Credencial UAT
- Credencial vazada invalidada/rotacionada: sim para o escopo local UAT.
- Método: revogação de sessões ativas de usuários UAT locais e criação de usuário UAT sintético novo.
- Sessões UAT antigas revogadas: 82.
- Senha/token/cookie impressos: não.
- Credenciais temporárias: somente `/tmp/apoema-m6-rerun/uat-credentials.json` com permissão restrita.

## StorageState
- Arquivo: `/tmp/apoema-uat-auth-state.json`.
- Criado fora do repo: True.
- Commitado: não.

## Browser auth
- Refresh no browser: 200.
- Rotas testadas: `/apoema`, `/apoema/chat`, `/apoema/assets`, `/apoema/settings`.
- Redirecionou para login: False.
- Evidência redigida: `raw/auth-rerun-probe-redacted.json`.

## API smoke autenticado
- API smoke autenticado OK: True.
- Artifacts OK: True.
- AI Chat OK: True.
- RAG OK: True.
- Designer OK: True.
- Evidência redigida: `raw/api-smoke-redacted.json`.

## Screenshots autenticados
- Criados: True.
- Quantidade: 12.
- Rotas: `/apoema`, `/apoema/chat`, `/apoema/assets`, `/apoema/settings`.
- Viewports: `390x844`, `1366x768`, `1920x1080`.
- Diretório: `screenshots/`.

## UI gate decision
READY_FOR_UI_STUBS

## Arquivos de evidência
- `m6-authenticated-e2e-rerun-findings.json`
- `m6-authenticated-e2e-rerun-gates.log`
- `maps/auth-rerun-matrix.tsv`
- `maps/api-smoke-rerun.tsv`
- `maps/ui-gate-rerun-decision.tsv`
- `raw/auth-rerun-probe-redacted.json`
- `raw/api-smoke-redacted.json`
- `raw/screenshots-redacted.json`
- `screenshots/*.png`

## Próxima fase recomendada
M6B_APOEMA_UI_STUBS
