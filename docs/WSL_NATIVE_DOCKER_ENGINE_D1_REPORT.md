# WSL Native Docker Engine D1 Report

## 1. Resumo Executivo

`INFRA-D1 -- Docker Engine nativo no WSL` foi executada como diagnostico e preparacao de migracao.

Status: `PARTIAL`.

Motivo:

- WSL esta em Ubuntu 24.04 com systemd ativo;
- Docker atual nao e nativo da distro;
- `docker` e `docker-compose` resolvem para symlinks do Docker Desktop em `/mnt/wsl/docker-desktop/...`;
- daemon atual reporta `Operating System: Docker Desktop`;
- Docker CE oficial nao esta instalado via apt;
- `sudo -n` nao esta disponivel nesta sessao, entao a instalacao segura via apt nao foi executada.

Nenhum volume, dado, `.env`, migration, backend funcional, frontend visual ou dependencia do projeto foi alterado.

## 2. Estado Inicial

Repositorio:

- branch: `main...origin/main [ahead 1]`
- staged: nenhum item observado em `git diff --cached --name-status`
- worktree: ja estava sujo antes desta boundary
- arquivos frontend/docs/backend/testes ja estavam modificados ou untracked por boundaries anteriores

Confirmacao:

- nao foi feito commit;
- nao foi executado `git add`;
- nao foi executado `git reset`;
- nao foi executado `git checkout`.

## 3. Motivo da Migracao

O objetivo tecnico e remover a dependencia de Docker Desktop/Windows integration para desenvolvimento local dentro da distro WSL.

Estado desejado:

- `docker` Linux nativo em `/usr/bin/docker`, instalado por pacote apt da Docker Inc.;
- daemon `dockerd` gerenciado por systemd dentro do WSL;
- Compose plugin nativo;
- Postgres/Redis do projeto rodando no Docker Engine nativo;
- backend FastAPI e frontend validados sem depender de Docker Desktop.

## 4. Distro WSL Detectada

Ambiente detectado:

- distro: Ubuntu 24.04.4 LTS, Noble Numbat
- kernel: WSL2 Linux `6.18.33.1-microsoft-standard-WSL2`
- usuario: `estevaoqualityadm`
- grupos: inclui `sudo` e `docker`
- WSL: `Ubuntu-24.04` rodando em versao 2
- espaco livre em `/`, `/var` e `/home`: aproximadamente 933 GiB disponivel

Observacao:

- `docker-desktop` tambem aparece como distro WSL em execucao, confirmando que Docker Desktop ainda esta ativo no ambiente Windows/WSL.

## 5. Systemd

Systemd:

- PID 1: `systemd`
- `systemctl is-system-running`: `running`
- `systemctl`: disponivel em `/usr/bin/systemctl`
- `service`: disponivel em `/usr/sbin/service`

Conclusao:

- a distro suporta ativar Docker Engine nativo com `systemctl enable --now docker` apos instalacao.

## 6. Docker Antes

Docker atual:

- `command -v docker`: `/usr/bin/docker`
- `command -v docker.exe`: `/Docker/host/bin/docker.exe`
- `/usr/bin/docker`: symlink para `/mnt/wsl/docker-desktop/cli-tools/usr/bin/docker`
- `/usr/bin/docker-compose`: symlink para `/mnt/wsl/docker-desktop/cli-tools/usr/local/lib/docker/cli-plugins/docker-compose`
- plugins em `/usr/local/lib/docker/cli-plugins`: symlinks para `/mnt/wsl/docker-desktop/...`
- `docker info`: `Operating System: Docker Desktop`
- `docker version`: `Server: Docker Desktop 4.77.0`
- contexto `desktop-linux`: presente
- daemon nativo systemd `docker`: `inactive`

Classificacao:

- Docker nativo: nao confirmado;
- Docker Desktop/Windows dependency: sim;
- Docker socket atual: ativo, mas associado ao Docker Desktop;
- Compose plugin atual: funcional, mas vindo do Docker Desktop;
- Docker Windows em PATH: detectado como `docker.exe`, nao usado para validacao final.

## 7. Docker Depois

Nao houve instalacao nesta sessao porque `sudo -n` retornou indisponivel.

Estado depois:

- Docker continua dependente do Docker Desktop;
- Docker Engine nativo ainda precisa ser instalado/ativado manualmente;
- nenhum pacote foi removido;
- nenhum volume foi apagado;
- nenhum dado foi migrado.

## 8. Metodo de Instalacao Escolhido

Metodo recomendado:

- Docker Engine oficial via repositorio apt da Docker Inc. para Ubuntu;
- Compose plugin oficial `docker-compose-plugin`;
- systemd para gerenciar o servico Docker dentro do WSL.

Nao recomendado:

- `snap`;
- `docker.io` do Ubuntu;
- Docker Desktop;
- `docker.exe`;
- copiar volumes automaticamente do Docker Desktop.

## 9. Pacotes Instalados

Pacotes Docker detectados via dpkg:

- nenhum pacote Docker CE instalado;
- `docker.io`: nao instalado;
- `podman-docker`: nao instalado.

Repositorios:

- nenhum `download.docker.com` detectado em `/etc/apt/sources.list.d`;
- somente fonte Ubuntu padrao observada.

Pacotes a instalar manualmente:

- `ca-certificates`
- `curl`
- `gnupg`
- `docker-ce`
- `docker-ce-cli`
- `containerd.io`
- `docker-buildx-plugin`
- `docker-compose-plugin`

## 10. Servico Docker

Servico atual:

- `systemctl is-active docker`: `inactive`

Depois da instalacao manual:

```bash
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager --lines=80
```

## 11. Grupo Docker e Relogin

Usuario atual:

- `estevaoqualityadm` ja pertence ao grupo `docker`.

Ainda assim, depois de instalar o Engine nativo pode ser necessario:

```bash
getent group docker || sudo groupadd docker
sudo usermod -aG docker "$USER"
```

Observacao:

- se o grupo for alterado, fechar e reabrir a sessao WSL;
- nao usar `chmod 666 /var/run/docker.sock`.

## 12. Compose Plugin

Compose atual:

- `Docker Compose version v5.1.4`, mas vindo de symlink do Docker Desktop.

Compose desejado:

- `docker compose version` resolvendo pelo plugin apt nativo, sem symlink para `/mnt/wsl/docker-desktop`.

Validacao esperada:

```bash
which docker
docker compose version
ls -l /usr/local/lib/docker/cli-plugins /usr/libexec/docker/cli-plugins 2>/dev/null || true
```

## 13. Validacao Hello-World

Nao executada como criterio final porque o Docker atual usa Docker Desktop.

Apos instalacao nativa, validar:

```bash
docker run --rm hello-world
```

Criterio:

- container roda sem `sudo`;
- `docker info` nao menciona Docker Desktop;
- `Docker Root Dir` aponta para Linux/WSL, normalmente `/var/lib/docker`.

## 14. Servicos do Projeto Encontrados

Nao foi usada a configuracao Compose atual como validacao final porque o daemon ativo e Docker Desktop.

Em auditoria anterior do projeto, os servicos esperados sao:

- `postgres`
- `redis`
- `app`

Apos Docker nativo:

```bash
docker compose config --services
```

Nao imprimir `docker compose config` completo se houver risco de expor variaveis.

## 15. Postgres/Redis

Estado atual observado:

- portas `5432` e `6379` estao abertas;
- containers do projeto podem estar rodando via Docker Desktop.

Status INFRA-D1:

- Postgres nativo WSL: nao validado;
- Redis nativo WSL: nao validado.

Apos instalacao nativa:

```bash
docker compose up -d postgres redis
docker compose ps
ss -ltnp | egrep ':5432|:6379' || true
```

Nao remover volumes.

## 16. Backend

Estado observado:

- porta `8000` estava ocupada por `uvicorn`;
- backend existente nao foi iniciado nem encerrado por esta boundary.

Status INFRA-D1:

- backend sobre Docker nativo: nao validado.

Apos Docker nativo e Postgres/Redis:

```bash
curl -i --max-time 10 http://127.0.0.1:8000/health || true
curl -i --max-time 10 http://127.0.0.1:8000/api/v1/auth/refresh || true
```

## 17. Frontend

Frontend WSL nativo ja havia sido validado em boundaries anteriores.

Nesta boundary:

- build/preview contra Docker nativo nao foi executado como criterio final, porque Docker nativo ainda nao foi instalado.

Apos Docker nativo:

```bash
source "$HOME/.nvm/nvm.sh"
nvm use 22.22.3
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform
timeout 180 npm run build
```

## 18. O Que Nao Foi Feito

- nao foi usado Docker Desktop como validacao final;
- nao foi usado `docker.exe`;
- nao foi instalado pacote sem `sudo` seguro;
- nao foi removido pacote;
- nao foi executado `docker system prune`;
- nao foi executado `docker volume prune`;
- nao foi apagado `/var/lib/docker`;
- nao foi migrado volume do Docker Desktop;
- nao foram alterados backend, frontend visual, migrations ou dependencias;
- nao foi lido `.env`.

## 19. Riscos Remanescentes

- Docker Desktop ainda injeta symlinks em `/usr/bin/docker` e plugins enquanto sua integracao WSL estiver ativa.
- Instalar Docker Engine nativo exige `sudo` interativo ou uma sessao com permissao administrativa.
- Apos instalar Docker nativo, pode ser necessario desativar a integracao Docker Desktop para esta distro ou garantir precedencia dos binarios nativos.
- Volumes do Docker Desktop nao devem ser migrados automaticamente; se dados forem necessarios, abrir boundary separada.
- Portas `5432`, `6379` e `8000` podem estar ocupadas por processos/containers existentes antes da migracao.

## 20. Comandos de Uso Diario

Depois de concluir a instalacao nativa:

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
npm run preview -- --host 127.0.0.1 --port 4173
```

## 21. Comandos Proibidos

Nao executar sem boundary/autorizacao explicita:

```bash
docker system prune
docker volume prune
sudo rm -rf /var/lib/docker
docker compose down -v
```

Nao usar:

```bash
docker.exe
```

## 22. Proximo Passo Recomendado

Abrir uma execucao operacional assistida com `sudo` disponivel para concluir `INFRA-D1`.

Sequencia recomendada:

1. Executar os comandos do runbook `docs/LOCAL_DOCKER_WSL_NATIVE_RUNBOOK.md`.
2. Instalar Docker CE oficial via apt.
3. Ativar `docker.service` com systemd.
4. Confirmar que `docker` nao aponta para `/mnt/wsl/docker-desktop`.
5. Subir `postgres` e `redis`.
6. Validar backend e frontend.

## 23. Follow-up D1B

`INFRA-D1B` foi iniciada como follow-up com sudo interativo permitido, mas tambem ficou `PARTIAL`.

Motivo:

- `sudo -v` abriu prompt interativo, mas a autenticacao nao foi concluida nesta sessao;
- a verificacao retornou `SUDO_CACHE_NOT_AVAILABLE_AFTER_AUTH`;
- por regra da boundary, nenhuma remocao de symlink, instalacao apt, ativacao de servico ou validacao Docker foi executada.

Relatorio dedicado:

- [WSL_NATIVE_DOCKER_ENGINE_D1B_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1B_REPORT.md)

## 24. Resolucao em D1C

`INFRA-D1C` concluiu a migracao com `GO`.

Resumo:

- instalacao via script temporario root-assistido executado manualmente pelo operador;
- Docker CE oficial instalado via apt;
- `docker` agora resolve para `/usr/bin/docker`, sem symlink para Docker Desktop;
- `docker info` reporta `Operating System: Ubuntu 24.04.4 LTS`;
- `Docker Root Dir`: `/var/lib/docker`;
- `docker.service` e `containerd.service` ativos e enabled;
- Compose plugin nativo funciona;
- `hello-world` passou;
- Postgres/Redis subiram no daemon nativo;
- backend `/health` respondeu 200;
- frontend build e preview passaram.

Relatorio dedicado:

- [WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/WSL_NATIVE_DOCKER_ENGINE_D1C_REPORT.md)
