# Runtime Access Fix — 2026-06-25

1. Status
- PARTIAL-GO

2. Causa raiz
- O Chrome do Windows estava apontando para o IP da bridge Docker `172.18.0.1:5173`, que não é um endereço público para o navegador do Windows.
- O frontend Vite está rodando no host WSL, não em container, e escuta em `0.0.0.0:5173`.
- Neste ambiente, o Windows não conseguiu alcançar `localhost:5173`, `127.0.0.1:5173` nem os IPs WSL testados via PowerShell, então o caminho Windows→Vite segue instável fora do browser-tool desta sessão.
- A rota estável validada por browser foi o app servido no container em `http://localhost:8080/apoema`.

3. Onde o Vite roda: WSL host/container
- WSL host.
- Processo ativo: `node .../frontend/itam-platform/node_modules/.bin/vite --host 0.0.0.0 --port 5173`.

4. Porta real do Vite
- 5173.

5. Bind real do Vite
- `0.0.0.0:5173`.

6. URL que funciona dentro do WSL
- `http://172.18.0.1:5173/apoema` retornou `200 OK` no curl do WSL.
- `http://localhost:8080/apoema` também carregou corretamente no browser-tool desta sessão.

7. URL que funciona no Windows
- Não validada com sucesso por PowerShell nesta sessão.
- URL recomendada para nova tentativa no browser Windows: `http://localhost:8080/apoema`.

8. Backend healthy: sim/não
- Sim.
- `GET /health` e `GET /health/ready` em `http://localhost:8080` e `http://172.18.0.1:8080` responderam `200`.

9. Containers healthy: sim/não
- Sim.
- `app`, `postgres` e `redis` estavam `healthy` no `docker compose ps`.

10. Correção aplicada
- Nenhuma alteração de código/runtime foi necessária para o backend ou frontend visual.
- A correção efetiva desta sessão foi documental: consolidar o runtime correto e o URL de acesso validado.

11. Arquivos alterados
- `docs/audit/runtime-access-fix/RUNTIME_ACCESS_FIX_20260625.md`
- `docs/audit/runtime-access-fix/runtime-access-findings.json`
- `docs/audit/runtime-access-fix/runtime-access-gates.log`

12. Validações executadas
- `docker compose ps`
- `docker compose logs --tail=120 app`
- `ss -ltnp`
- `ps aux | grep -E 'vite|uvicorn|node|npm|pnpm|yarn'`
- `hostname -I`
- `curl` em múltiplas bases para `/apoema`
- `curl` em múltiplas bases para `/health` e `/health/ready`
- `powershell.exe` / `Test-NetConnection` para `localhost`, `127.0.0.1` e IPs WSL/Docker
- `browser_navigate` para `http://localhost:8080/apoema`
- `browser_console`
- `PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests -v`
- `.venv/bin/python -m ruff check backend tests scripts`
- `.venv/bin/python -m compileall -q backend/app backend/alembic tests scripts`
- `cd frontend/itam-platform && npm run build`
- `git diff --check`

13. Smoke Windows executado
- Sim, mas com falha.
- `localhost:5173` falhou.
- `127.0.0.1:8080` falhou.
- `localhost:8080` não foi confirmado com sucesso via PowerShell nesta sessão.

14. URL final recomendada para abrir no navegador
- `http://localhost:8080/apoema`

15. Push executado
- Não.

16. Observações finais
- `172.18.0.1` não deve ser usado no Chrome do Windows como URL principal.
- Se for obrigatório manter o Vite dev server como alvo do Chrome Windows, será necessário um ajuste adicional de acessibilidade de rede fora do aplicativo (portproxy/forward de host), porque o processo já está bindado corretamente no WSL, mas o Windows não conseguiu alcançá-lo diretamente nesta sessão.
