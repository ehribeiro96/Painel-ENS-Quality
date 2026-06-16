# QA-C2 — Controlled Backend HTTP Runtime Validation

Data/hora: 2026-06-16

Branch: `main`

Status: `GO`

## 1. Resumo executivo

Validação HTTP controlada executada para fechar a pendência do `QA-C1`.

Resultado: `GO`.

O backend temporário subiu em sessão persistente na porta `8000`, `/health` respondeu `200`, `/assinaturas/` respondeu `200`, `/admin/` redirecionou para `/admin/login`, `/admin/login` respondeu `200`, e CSP real por header foi validada sem Google Fonts, sem `unsafe-eval` e sem `style-src'self'` malformado.

Nenhum `git add`, commit ou push foi executado.

## 2. Estado git

- Branch: `main`
- Divergência: `main...origin/main [ahead 15]`
- Stage inicial: vazio
- Stage final: vazio
- Untracked remanescentes: preservados fora do escopo

## 3. Docker compose ps antes/depois

Antes:

- Sem serviços ativos listados por `docker compose ps`.

Depois de subir dependências permitidas:

- `painel-ens-quality-postgres-1`: `Up`, `healthy`, porta `5432`
- `painel-ens-quality-redis-1`: `Up`, `healthy`, porta `6379`

Docker Engine:

- Server Version: `29.5.3`
- Storage Driver: `overlayfs`
- Operating System: `Ubuntu 24.04.4 LTS`
- Docker Root Dir: `/var/lib/docker`

Postgres/Redis foram deixados rodando conforme boundary; não foi executado `docker compose down -v`, prune ou remoção de volumes.

## 4. Porta usada

- Porta usada: `8000`
- Diagnóstico inicial: sem listener identificado por `ss -ltnp`.

Observação: a primeira tentativa em background não persistiu após o shell encerrar. A validação efetiva foi feita com `uvicorn` em sessão persistente foreground.

## 5. Backend startup

Backend temporário:

```bash
PYTHONPATH=backend .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Variáveis de runtime usadas:

- `AI_CHAT_PROVIDER=ollama-lan`
- `AI_PROVIDER=ollama-lan`
- `OLLAMA_BASE_URL` apontando para o runtime LAN autorizado
- `OLLAMA_MODEL=qwen3:1.7b-64k`
- `OLLAMA_ALLOWED_HOSTS` com hosts permitidos
- `OLLAMA_TIMEOUT_SECONDS=120`

Startup observado:

- Database wait: `ok`
- Redis wait: `ok`
- Migrations: `up_to_date`
- Bootstrap admin: `ok`
- Frontend dist: pronto
- Legacy mount: `ok`

## 6. `/health`

Resultado:

- HTTP `200 OK`
- Body indicou `status: ok`
- `frontend_ready: true`
- `legacy_mounts`: `/admin`, `/assinaturas`
- Startup completo com Postgres e Redis OK

## 7. `/assinaturas/`

Resultado:

- HTTP `200 OK`
- Template legado público renderizado.
- Assets locais referenciados: Bootstrap local, Bootstrap Icons local, `templatemo-topic-listing.css`, favicon local.

## 8. `/admin/`

Resultado:

- HTTP `302 Found`
- `Location: /admin/login`

Comportamento esperado para rota administrativa sem sessão autenticada.

## 9. `/admin/login`

Resultado:

- HTTP `200 OK`
- Tela legada de login renderizada.
- Assets locais referenciados.

## 10. CSP real

Headers observados nas rotas legadas:

- `Content-Security-Policy`
- `Content-Security-Policy-Report-Only`

Política enforce observada:

```text
default-src 'self'; base-uri 'self'; object-src 'none'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'self'
```

Política report-only observada:

```text
default-src 'self'; base-uri 'self'; object-src 'none'; img-src 'self' data: https:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'self'
```

## 11. Google Fonts

Resultado: `PASS`.

- `fonts.googleapis.com`: ausente.
- `fonts.gstatic.com`: ausente.

## 12. `unsafe-eval`

Resultado: `PASS`.

- `unsafe-eval`: ausente.

## 13. `style-src` malformado

Resultado: `PASS`.

- `style-src'self'`: ausente.
- `style-src 'self'`: presente e bem formado.

## 14. Screenshots

Não executado.

Motivo: a boundary exigia validação HTTP/CSP; smoke headless era opcional e não necessário para fechar o bloqueio de `QA-C1`.

## 15. Scanner redigido

Escopo:

- Log temporário `/tmp/painel-ens-qa-c2-backend-8000.log`

Resultado:

- `FILES_SCANNED`: 1
- `FILES_WITH_MATCHES`: 1
- Matches classificados como nomes de variáveis ou flags de configuração (`*_set`) e identificadores genéricos.
- Nenhum valor real de segredo foi impresso.
- Nenhum risco real detectado.

## 16. Processos encerrados

- Backend temporário `uvicorn` encerrado.
- Porta `8000` liberada.
- Arquivo PID temporário em `/tmp` removido conforme procedimento da boundary.
- Postgres e Redis permaneceram rodando e `healthy`.

## 17. Decisão final

`GO`

Critérios atendidos:

- Backend controlado subiu.
- `/health` retornou `200`.
- `/assinaturas/` retornou `200`.
- `/admin/` retornou `302` para `/admin/login`.
- `/admin/login` retornou `200`.
- CSP real presente.
- Sem Google Fonts em CSP.
- Sem `unsafe-eval` em CSP.
- Sem `style-src'self'` malformado.
- Sem segredo detectado.
- Sem alteração de código.
- Sem stage, commit ou push.

## 18. Próxima boundary recomendada

Se o objetivo for publicar os commits acumulados, o próximo passo é uma decisão explícita de push/release.

Se o foco for robustez antes de push, seguir para `B6` com testes/infra isolados.
