# QA-C1 — Post-Commit Integration Validation

Data/hora: 2026-06-16

Branch: `main`

Status: `PARTIAL`

## 1. Resumo executivo

Validação pós-commit executada sem `git add`, sem commit, sem push e sem alteração de código. O stage inicial e final permaneceram vazios.

Resultado geral: `PARTIAL`.

Motivo da ressalva: o backend HTTP local em `127.0.0.1:8000` não respondeu durante `health` e smoke das rotas legadas, então `/assinaturas/` e `/admin/` não puderam ser validadas por HTTP nesta boundary. Backend compile, testes críticos, frontend build, Docker Engine nativo e Ollama LAN/Qwen3 passaram.

## 2. Estado git

- Branch: `main`
- Divergência: `main...origin/main [ahead 15]`
- Stage inicial: vazio
- Stage final: vazio
- Untracked remanescentes: presentes, mantidos fora do escopo

## 3. Últimos commits observados

- `d0fb175 docs(audit): document legacy assets triage`
- `b76c5c4 chore(legacy): track required legacy assets`
- `b77cc95 fix(legacy): remove external font dependency`
- `36ba624 docs(audit): document ambiguous remainder triage`
- `63ce5e1 test(security): cover icon sanitization`

## 4. Compileall

Comando:

```bash
PYTHONPATH=backend timeout 120 .venv/bin/python -m compileall -q backend/app tests
```

Resultado: `PASS`.

## 5. Testes backend

Grupo AI Chat/security:

- Primeira execução com captura padrão falhou antes de rodar testes por bug conhecido de cleanup/captura do pytest: `FileNotFoundError` em `_pytest/capture.py`.
- Retry com `-s`: `58 passed, 1 warning`.
- Warning observado: `starlette.middleware.wsgi` depreciado.

Grupo imports:

- Primeira execução com captura padrão falhou antes de rodar testes pelo mesmo bug conhecido de cleanup/captura.
- Retry com `-s`: `32 passed`.

Classificação: `PASS COM RESSALVA OPERACIONAL` por bug de captura contornado com retry permitido pela boundary.

## 6. Frontend build

Comando executado com `nvm use 22.22.3`:

```bash
timeout 180 npm run build
```

Resultado: `PASS`.

Resumo:

- `tsc --noEmit` passou.
- `vite build` passou.
- Bundle gerado com 1818 módulos transformados.

## 7. Docker/backend health

Docker:

- Server Version: `29.5.3`
- Storage Driver: `overlayfs`
- Operating System: `Ubuntu 24.04.4 LTS`
- Docker Root Dir: `/var/lib/docker`

Compose:

- `docker compose ps` não listou serviços ativos.

Backend health:

- `curl -i --max-time 10 http://127.0.0.1:8000/health` terminou em timeout.

Classificação: `PARTIAL` por backend local offline/não responsivo.

## 8. Ollama LAN/Qwen3

Endpoint validado:

- `http://192.168.0.103:11434/v1/chat/completions`

Modelo:

- `qwen3:1.7b-64k`

Resultado:

- HTTP status: `200`
- Conteúdo: resposta esperada contendo `OK via QA-C1.`
- `HAS_OK`: `True`
- `HAS_THINK_TAG`: `False`

Classificação: `PASS`.

## 9. Legacy routes/CSP

Rotas testadas:

- `http://127.0.0.1:8000/assinaturas/`
- `http://127.0.0.1:8000/admin/`

Resultado:

- Ambas terminaram em timeout por backend local não responsivo.
- CSP não pôde ser validada por header HTTP nesta boundary.

Classificação: `PARTIAL` por runtime HTTP offline.

## 10. Scanner redigido

Escopo:

- Arquivos versionados alterados em `origin/main..HEAD`.
- `.env`, bancos, dumps e binários sensíveis foram excluídos da leitura.
- O scanner imprimiu somente nomes de arquivos, padrões e classificação, sem linhas nem valores.

Resultado:

- `FILES_SCANNED`: 200
- `FILES_WITH_MATCHES`: 62
- Achados classificados como nomes de variáveis, placeholders, literais de teste/documentação, configuração Ollama documentada ou falso positivo.
- Nenhum valor real de segredo foi impresso.
- Nenhum risco real detectado.

## 11. Untracked remanescentes

Continuam presentes e fora do escopo:

- `.github/workflows/docker-build-push.yml`
- `_audit_findings/`
- `_cleanup_backup_manifest.md`
- `_migration_proposals/`
- `ai-lab/`
- `assets/legacy/`
- `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`
- ícones extras não versionados em `assets/static/icons/`
- relatórios antigos em `docs/` e `docs/audit/`
- screenshots antigas
- `frontend/package-lock.json`
- `imports/`
- amostras `docx_*` e `pptx_*`
- testes untracked remanescentes

Nenhum desses arquivos foi stageado, removido ou alterado por correção nesta boundary.

## 12. Decisão final

`PARTIAL`

Critérios aprovados:

- Compileall passou.
- Testes críticos passaram no retry permitido.
- Frontend build passou.
- Docker Engine nativo está ativo.
- Ollama LAN/Qwen3 passou.
- Stage inicial/final vazio.
- Nenhum segredo detectado.
- Nenhum push/commit/stage executado.

Ressalva:

- Backend local estava offline/não responsivo em `127.0.0.1:8000`, impedindo health e smoke HTTP/CSP das rotas legadas.

## 13. Próxima boundary recomendada

Antes de push, executar uma boundary curta de runtime HTTP se for necessário fechar `GO` completo:

- subir backend local de forma controlada;
- validar `/health`;
- validar `/assinaturas/` e `/admin/`;
- validar headers CSP reais;
- encerrar qualquer processo temporário iniciado.

Se o push não exigir smoke HTTP local nesta máquina, a próxima boundary pode ser `B6` para testes/infra isolados.
