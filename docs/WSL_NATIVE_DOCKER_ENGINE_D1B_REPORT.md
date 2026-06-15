# WSL Native Docker Engine D1B Report

## 1. Resumo Executivo

`INFRA-D1B -- Docker Engine nativo no WSL com sudo interativo` foi iniciada, mas ficou `PARTIAL`.

Motivo: a etapa obrigatoria `sudo -v` nao concluiu autenticacao nesta sessao. O prompt interativo apareceu, ficou aguardando senha e a verificacao final retornou `SUDO_CACHE_NOT_AVAILABLE_AFTER_AUTH`.

Por regra da boundary, a execucao foi interrompida antes de qualquer alteracao de sistema.

Nao foram removidos symlinks, pacotes, volumes, arquivos do projeto, dados Docker, migrations, dependencias frontend ou configuracoes sensiveis.

## 2. Estado Inicial

Repositorio:

- branch: `main...origin/main [ahead 1]`
- staged: nenhum item observado em `git diff --cached --name-status`
- worktree: ja estava sujo antes desta boundary
- arquivos docs de auditoria e Docker ja estavam untracked/modificados por boundaries anteriores

Confirmacao:

- nao foi feito commit;
- nao foi executado `git add`;
- nao foi executado `git reset`;
- nao foi executado `git checkout`.

## 3. Evidencia de Dependencia Docker Desktop Antes

Esta execucao parou na FASE 1 por falha de autenticacao sudo, antes da auditoria Docker detalhada da FASE 2.

A evidencia imediatamente anterior, registrada em `INFRA-D1`, permanece como base operacional:

- `/usr/bin/docker` apontava para `/mnt/wsl/docker-desktop/cli-tools/usr/bin/docker`;
- `/usr/bin/docker-compose` apontava para `/mnt/wsl/docker-desktop/.../docker-compose`;
- `docker info` reportava `Operating System: Docker Desktop`;
- Docker CE oficial nao estava instalado via apt;
- daemon `docker.service` nativo estava inativo.

Conclusao: antes da instalacao nativa, a distro ainda dependia do Docker Desktop.

## 4. Symlinks Removidos

Nenhum symlink foi removido.

Motivo: a boundary exigia `sudo -v` funcional antes de alteracoes de sistema. A autenticacao sudo nao foi obtida nesta sessao.

## 5. Pacotes Instalados

Nenhum pacote foi instalado.

Nao foram executados:

- `apt-get remove`;
- `apt-get install`;
- adicao de repositorio Docker apt;
- alteracao de keyrings apt.

## 6. Servico Docker Systemd

Systemd da distro foi confirmado:

- PID 1: `systemd`
- `systemctl is-system-running`: `running`

O servico Docker nativo nao foi instalado nem ativado nesta execucao.

## 7. Grupo Docker

Usuario atual:

- `estevaoqualityadm`
- grupos incluem `sudo` e `docker`

Nenhuma alteracao de grupo foi feita. Relogin nao foi disparado por esta execucao.

## 8. Docker Depois

Como nenhuma alteracao de sistema foi aplicada, o estado Docker deve ser considerado inalterado em relacao a `INFRA-D1`:

- Docker nativo no WSL: nao confirmado;
- dependencia Docker Desktop: ainda considerada presente;
- Compose plugin nativo: nao confirmado;
- daemon Docker via systemd: nao confirmado.

## 9. Evidencia de Independencia do Docker Desktop

Nao houve evidencia de independencia nesta execucao.

`docker info` final nativo nao foi executado porque a instalacao foi interrompida antes de modificar symlinks, instalar Docker CE ou ativar `docker.service`.

## 10. Compose Plugin

Compose plugin nativo nao foi instalado nem validado.

O Compose funcional observado antes da boundary vinha de symlink do Docker Desktop, conforme `INFRA-D1`.

## 11. Hello-World

`docker run --rm hello-world` nao foi executado.

Motivo: o criterio da boundary exigia validar `hello-world` somente depois de confirmar Docker Engine nativo.

## 12. Postgres/Redis

`postgres` e `redis` do projeto nao foram iniciados nesta execucao.

Nao foram executados:

- `docker compose stop postgres redis`;
- `docker compose up -d postgres redis`;
- `docker compose logs`.

Nenhum volume foi removido.

## 13. Backend Health

Backend `/health` nao foi revalidado nesta execucao.

Motivo: a boundary parou na FASE 1 antes de preparar Docker nativo e antes das validacoes de app.

## 14. Auth Refresh Sem Sessao

`/api/v1/auth/refresh` nao foi revalidado nesta execucao.

Nenhuma credencial foi enviada ou solicitada.

## 15. Frontend Build/Preview

Frontend nao foi buildado nem servido nesta execucao.

Nao foram executados:

- `npm run build`;
- `npm run preview`;
- validacao HTTP de rotas.

`package-lock.json` nao foi alterado.

## 16. O Que Nao Foi Feito

- nao foi removido Docker Desktop do Windows;
- nao foi removido symlink local;
- nao foi instalado Docker Engine;
- nao foi instalado Compose plugin;
- nao foi usado Snap Docker;
- nao foi usado `curl | bash`;
- nao foi executado prune;
- nao foi executado `docker compose down -v`;
- nao foi apagado `/var/lib/docker`;
- nao foram apagados volumes;
- nao foram alterados backend, frontend visual, migrations ou dependencias;
- nao foi lido `.env`;
- nao foi alterado `~/.hermes/config.yaml`.

## 17. Riscos Remanescentes

- A distro ainda deve ser tratada como dependente do Docker Desktop ate prova contraria.
- O prompt sudo usado por esta ferramenta pode nao estar visivel ou acionavel pelo operador.
- Enquanto Docker Desktop continuar injetando symlinks, `docker` pode resolver para `/mnt/wsl/docker-desktop`.
- Postgres/Redis nativos no WSL ainda nao foram validados.
- Backend e frontend ainda nao foram revalidados contra Docker Engine nativo.

## 18. Comandos de Uso Diario

Apos concluir a instalacao nativa com sudo funcional:

```bash
docker version
docker info
docker compose version
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality
docker compose up -d postgres redis
PYTHONPATH=backend .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
cd frontend/itam-platform
source "$HOME/.nvm/nvm.sh"
nvm use 22.22.3
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
```

## 19. Comandos Proibidos

Nao executar sem boundary/autorizacao explicita:

```bash
docker system prune
docker volume prune
docker compose down -v
sudo rm -rf /var/lib/docker
```

Nao usar:

```bash
docker.exe
```

## 20. Proximo Passo Recomendado

Reexecutar `INFRA-D1B` com uma sessao em que `sudo -v` seja autenticado antes da instalacao.

Opcao operacional segura:

1. Em um terminal WSL visivel para o operador, executar `sudo -v`.
2. Sem expor senha, confirmar que `sudo -n true` retorna sucesso.
3. Retomar a boundary a partir da auditoria Docker e remocao controlada dos symlinks locais para Docker Desktop.

## 21. Resolucao em D1C

`INFRA-D1C` substituiu a dependencia de cache sudo por um fluxo root-assistido:

- Codex gerou scripts temporarios auditaveis em `/tmp`;
- o operador executou os scripts manualmente com `sudo bash` no terminal WSL real;
- Docker Engine nativo foi instalado via apt oficial;
- symlinks locais residuais para Docker Desktop foram removidos;
- `docker info` passou a reportar `Operating System: Ubuntu 24.04.4 LTS`;
- `Docker Root Dir` ficou em `/var/lib/docker`;
- `hello-world`, Postgres/Redis, backend e frontend foram validados.

Relatorio dedicado:

- [WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md)
