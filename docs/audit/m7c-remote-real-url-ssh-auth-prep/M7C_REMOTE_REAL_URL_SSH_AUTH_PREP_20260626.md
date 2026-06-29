# M7C — Remote Real URL and SSH Auth Prep

## 1. Status
PARTIAL-GO: REAL_GITHUB_REMOTE_URL não foi definido e o SSH para GitHub retornou Permission denied (publickey). Gates técnicos passaram. Push não executado.

## 2. Objetivo
Corrigir origin real, validar SSH/fetch e preparar autorização futura de push, sem executar push.

## 3. Estado inicial
- Branch: main
- Divergência antes: 0	161 (0 atrás / 161 à frente)
- Stage: limpo
- Tracked diff: vazio
- Origin antes: git@github.com:OWNER/REPO.git
- REAL_GITHUB_REMOTE_URL presente: não

## 4. Remote
- Origin depois: git@github.com:OWNER/REPO.git
- Placeholder corrigido: não
- URL validada: não
- Observação: origin não foi alterado porque REAL_GITHUB_REMOTE_URL não estava definido explicitamente.

## 5. DNS/rede
- github.com resolvido via getent/ping: sim
- nslookup: indisponível no ambiente (/usr/bin/bash: nslookup: command not found)

## 6. SSH agent/key
- Chave esperada encontrada: sim
- Chave carregada no agent: sim
- Artefato: raw/ssh-diagnostics-redacted.txt

## 7. SSH GitHub auth
- ssh -T git@github.com autenticou: não
- Classificação: SSH_PERMISSION_DENIED_PUBLICKEY

## 8. ls-remote/fetch
- git ls-remote executado: não
- git ls-remote OK: não
- git fetch origin --prune executado: não
- git fetch origin --prune OK: não
- Motivo do skip: REAL_GITHUB_REMOTE_URL ausente e SSH GitHub não autenticado.

## 9. Divergência final
- origin/main...HEAD: 0	161
- Atrás: 0
- À frente: 161

## 10. Gates técnicos
- git diff --check: OK
- PYTHONPATH=backend .venv/bin/python -m pytest -s -q: OK (336 passed, 22 skipped, 1 warning)
- .venv/bin/python -m ruff check backend tests scripts: OK
- .venv/bin/python -m compileall -q backend/app backend/alembic tests scripts: OK
- frontend/itam-platform npm run build com Node v22.22.3: OK
- Log: m7c-remote-real-url-ssh-auth-prep-gates.log

## 11. Segurança
- Segredos encontrados nos artefatos M7C: não; varredura final registrada em m7c-security-boundary-check.log.
- Storage state/cookies/tokens commitados: não
- Chave privada commitada: não

## 12. Push
- Push executado: não

## 13. Decisão
- PARTIAL_REMOTE_BLOCKED
- Motivo: remote real ausente; origin permanece placeholder; ssh -T git@github.com retornou Permission denied (publickey); ls-remote/fetch não foram executados.
- Próxima fase recomendada: MANUAL_PUSH_AUTHORIZATION após export explícito de REAL_GITHUB_REMOTE_URL e autorização SSH no GitHub.
