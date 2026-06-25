# Windows ⇄ WSL ⇄ Docker Runtime Diagnosis — Apoema

Data: 2026-06-25

## 1. Status
PARTIAL-GO

## 2. Sintoma observado
- `http://172.18.0.1:5173/apoema` no Chrome Windows deu timeout.
- `http://localhost:8080/apoema` no Windows deu `ERR_CONNECTION_RESET`.

## 3. Resultado dentro do WSL
- Vite está escutando em `0.0.0.0:5173`.
- Backend FastAPI está escutando em `0.0.0.0:8080`.
- `http://172.18.0.1:5173/apoema` responde `200 OK` com HTML do Vite.
- `http://localhost:8080/apoema` responde `200 OK` com HTML do frontend buildado pelo backend.
- `http://127.0.0.1:8080/apoema` dentro do WSL retorna `connection reset`.

## 4. Resultado via PowerShell/Windows
- `curl.exe http://127.0.0.1:5173/apoema` falhou com `Could not connect to server`.
- `curl.exe http://localhost:5173/apoema` falhou com `Could not connect to server`.
- `curl.exe http://127.0.0.1:8080/apoema` falhou com `Recv failure: Connection was reset`.
- `curl.exe http://localhost:8080/apoema` falhou com `Recv failure: Connection was reset`.
- `curl.exe http://192.168.0.80:5173/apoema` falhou com `Could not connect to server`.
- `curl.exe http://192.168.0.80:8080/apoema` falhou com `Could not connect to server`.
- `curl.exe http://172.18.0.1:5173/apoema` falhou com `Connection timed out`.
- `curl.exe http://172.18.0.1:8080/apoema` falhou com `Connection timed out`.

## 5. Resultado Docker
- `app`: healthy
- `postgres`: healthy
- `redis`: healthy
- Porta publicada do app no host do Docker: `0.0.0.0:8080->8080/tcp`
- `8080` está publicado pelo Docker
- `5173` não está publicado pelo Docker

## 6. Resultado Vite
- Processo ativo: `vite --host 0.0.0.0 --port 5173`
- Bind: `0.0.0.0:5173`
- Proxy configurado para `/api/v1 -> http://127.0.0.1:8080`

## 7. Resultado backend
- Backend ativo em `0.0.0.0:8080`
- `GET /health` responde `200 OK`
- `GET /health/ready` responde `200 OK`
- `GET /apoema` em `localhost:8080` retorna HTML do frontend buildado

## 8. Portproxy / firewall
- `netsh interface portproxy show all` revelou:
  - `127.0.0.1:8080 -> 172.16.0.2:18080`
  - `127.0.0.1:18086 -> 172.16.0.2:18085`
- `iphlpsvc` está `RUNNING`
- Windows mostra listener em `127.0.0.1:8080` com processo `svchost.exe`
- Não houve regra explícita de firewall encontrada para `WSL|Apoema|5173|8080`

## 9. Causa provável
M_MULTIPLE_CAUSES

Motivos:
1. O Windows não consegue alcançar o Vite em `5173`.
2. O Windows `localhost:8080` está entrando em um listener `svchost`/portproxy, mas o portproxy aponta para `172.16.0.2:18080`, enquanto nada está escutando em `18080` no WSL.
3. `172.18.0.1` é bridge Docker dentro do WSL; no Windows esse endereço não é um caminho confiável para browser.

## 10. URL funcional dentro do WSL
- `http://172.18.0.1:5173/apoema`
- `http://localhost:8080/apoema`

## 11. URL recomendada para Windows
- Após correção externa de rede/portproxy: `http://localhost:8080/apoema`

## 12. Comandos seguros para correção, se necessário
Sugestão apenas, não aplicada:
- Revisar/remover o portproxy atual de `127.0.0.1:8080 -> 172.16.0.2:18080`
- Recriar o encaminhamento para a porta realmente em uso no WSL/Docker
- Se a intenção for expor o Vite ao Windows, criar forwarding específico para `5173` ou usar o backend em `8080`

## 13. O que não foi alterado
- Nenhum arquivo de código
- Nenhum Docker Compose
- Nenhum Vite config
- Nenhuma migration
- Nenhuma autenticação/RBAC
- Nenhum segredo ou `.env`
