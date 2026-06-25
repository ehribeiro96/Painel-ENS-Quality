# Docker backend publish fix audit — 2026-06-25

1. Status: PARTIAL-GO
2. Causa classificada: host_wsl_ipv4_publish_mismatch; o backend funciona dentro do container e via IP do container, mas o caminho WSL/Windows para 127.0.0.1:8080 em IPv4 ainda falha com reset/timeout
3. Backend bind dentro do container: não é 127.0.0.1-only; o runtime responde em 127.0.0.1 dentro do container, em 172.18.0.4:8080 e também em ::1/localhost no WSL host
4. Docker publish antes/depois: inalterado, 0.0.0.0:8080->8080/tcp (e [::]:8080->8080/tcp) antes e depois
5. Resultado container interno: /health/ready = 200; /apoema = 200; /api/v1/auth/refresh = 401; /api/v1/auth/login = 422
6. Resultado WSL host via 127.0.0.1:8080: falha com ECONNRESET / Recv failure
7. Resultado WSL host via APP_IP:8080: 200 para /health/ready e /apoema em 172.18.0.4:8080
8. Resultado Vite proxy /api/v1/auth/refresh: ECONNRESET quando o target é http://127.0.0.1:8080; o problema não é auth, é a rota de transporte usada pelo proxy
9. Resultado Windows 127.0.0.1:8080: continua falhando com conexão encerrada/reset; Test-NetConnection pode reportar True, mas iwr recebe reset
10. Arquivos alterados: docs/audit/docker-backend-publish-fix/DOCKER_BACKEND_PUBLISH_FIX_20260625.md; docs/audit/docker-backend-publish-fix/docker-backend-publish-findings.json; docs/audit/docker-backend-publish-fix/docker-backend-publish-gates.log
11. Código de app alterado: não
12. Backend business logic alterado: não
13. Docker/infra dev alterado: não
14. Validações: docker compose ps; docker compose port app 8080; docker inspect ports/networks; curl de WSL para 127.0.0.1:8080, localhost:8080, APP_IP:8080, WSL_IP:8080; curl de Windows para 127.0.0.1:8080 e localhost:8080; container-local urllib para health/ready, apoema, auth/refresh
15. Próxima fase recomendada: corrigir o target do proxy dev para usar o caminho IPv6/localhost que de fato responde no WSL, ou reiniciar/controlar a camada WSL/Docker para tornar 127.0.0.1:8080 acessível em IPv4 para Windows/WSL

Notas de evidência:
- Dentro do WSL, `localhost:8080` responde via IPv6 `::1`, enquanto `127.0.0.1:8080` falha.
- O IP do container `172.18.0.4:8080` responde no WSL.
- O IP do WSL `192.168.0.80:8080` não responde do WSL nem do Windows.
- O problema atual é de caminho de rede/loopback, não de startup do FastAPI nem de health do container.
