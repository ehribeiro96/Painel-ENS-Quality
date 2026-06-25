# Windows ⇄ WSL portproxy fix audit — 2026-06-25

1. Status: PARTIAL-GO
2. Causa raiz: stale_windows_portproxy; Windows 127.0.0.1 listeners were pointing to an old WSL/container target and the corrected WSL target was not reachable from Windows in this environment
3. WSL IP usado: 192.168.0.80
4. Portproxy antes:
   - 127.0.0.1:8080 -> 172.16.0.2:18080
   - 127.0.0.1:18086 -> 172.16.0.2:18085
5. Portproxy depois:
   - 127.0.0.1:5173 -> 192.168.0.80:5173
   - 127.0.0.1:8080 -> 192.168.0.80:8080
   - 127.0.0.1:18086 -> 172.16.0.2:18085 (preserved)
6. Serviços/portas no WSL:
   - Vite listened on 0.0.0.0:5173 (node / frontend/itam-platform/node_modules/.bin/vite)
   - Docker compose app published 0.0.0.0:8080->8080/tcp and was healthy
   - postgres/redis healthy
7. Test-NetConnection antes/depois:
   - before: 5173 False, 8080 True
   - after: 5173 True, 8080 True
8. HTTP Windows antes/depois:
   - before: not working for the target URLs
   - after: browser/PowerShell requests still hit ERR_CONNECTION_RESET / underlying connection closed
9. HTTP WSL depois:
   - inside app container: http://127.0.0.1:8080/health/ready -> 200
   - inside app container: http://127.0.0.1:8080/apoema -> 200
   - from WSL shell to 127.0.0.1:5173 and 127.0.0.1:8080: connection reset by peer
10. Firewall criado/validado:
   - Apoema WSL Frontend 5173: Allow inbound TCP 5173
   - Apoema WSL Backend 8080: Allow inbound TCP 8080
11. URL final recomendada no Windows: not recommended yet; Windows still gets connection reset on 127.0.0.1:5173/apoema and 127.0.0.1:8080/health/ready
12. Código alterado: não
13. Backend alterado: não
14. Push executado: não

Notes:
- The portproxy entries were recreated against the current WSL IP as requested.
- The remaining blocker is outside app code: Windows-to-WSL reachability for the forwarded targets still resets in this session.
