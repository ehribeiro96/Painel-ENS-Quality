# Security Sanitization Report

Data: 2026-06-02

## Arquivos sanitizados

| Arquivo | Acao | Observacao |
|---|---|---|
| `.env.example` | Sanitizado | Senha admin e JWT secret foram trocados por placeholders seguros. |
| `.gitignore` | Atualizado | `.env`, `secrets/`, backups, evidencias, caches e artefatos locais ignorados. |
| `.dockerignore` | Atualizado | Segredos e artefatos locais excluidos do contexto Docker; templates `.docx` preservados. |
| `src/legacy/flask_app.py` | Endurecido | Removidos defaults sensiveis de admin, secret key e SMTP. |
| `scripts/create-local-secrets.ps1` | Endurecido | Gera secret local forte e placeholders, sem valores fixos fracos. |

## Secrets encontrados e tratados

- `.env.example` continha senha admin de exemplo e secret JWT fraco.
- `src/legacy/flask_app.py` continha fallback de senha admin, secret key e SMTP.
- `scripts/create-local-secrets.ps1` criava secrets locais fracos por padrao.

Valores nao foram reproduzidos neste relatorio. Recomenda-se rotacionar qualquer
credencial que tenha sido distribuida antes desta sanitizacao.

## Variaveis obrigatorias

- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `ADMIN_NAME`
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `ENS_SECRET_KEY` para legado em producao
- `ENS_ADMIN_PASS` para admin legado em producao
- `ENS_SMTP_USER` e `ENS_SMTP_PASSWORD` somente quando `ENS_SMTP_MODE=ON`

## Politica operacional

- `.env` real deve existir apenas localmente ou em secret manager.
- `secrets/` e backups locais nao devem ser empacotados.
- Senhas, tokens, cookies e connection strings reais nao devem aparecer em docs,
  testes, scripts ou logs.

## Riscos restantes

- O workspace local ainda possui `.env`, backups e evidencias ignoradas; eles nao
  devem ser copiados para bundle/release.
- O legado Flask ainda deve ser separado em config/auth/rendering em fase futura.
