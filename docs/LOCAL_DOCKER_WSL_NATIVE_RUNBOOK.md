# Local Docker WSL Native Runbook

Este runbook descreve como concluir e operar Docker Engine nativo dentro da distro WSL Ubuntu 24.04 para o projeto `Painel-ENS-Quality`.

## Estado Atual Pos-D1C

`INFRA-D1C` concluiu a migracao com `GO`.

Estado validado:

- `docker`: `/usr/bin/docker`;
- `Docker Root Dir`: `/var/lib/docker`;
- `Operating System`: `Ubuntu 24.04.4 LTS`;
- Compose plugin nativo: `/usr/libexec/docker/cli-plugins/docker-compose`;
- `docker.service` e `containerd.service`: ativos;
- `postgres` e `redis`: healthy no daemon nativo;
- backend `/health`: 200;
- frontend build/preview: OK.

## 1. Principios

- Usar Docker Engine Linux dentro do WSL.
- Nao depender de Docker Desktop.
- Nao usar `docker.exe`.
- Nao apagar volumes.
- Nao rodar comandos de prune sem autorizacao explicita.
- Nao imprimir `.env`, credenciais, URLs com senha ou tokens.

## 2. Autenticacao Sudo

Antes de iniciar a instalacao, valide que a mesma sessao que executara os comandos consegue usar `sudo`:

```bash
sudo -v
sudo -n true && echo SUDO_CACHE_OK
```

Se o prompt de `sudo` aparecer em uma PTY que o operador nao consegue controlar, pare a execucao e use um terminal WSL interativo real para concluir a boundary.

Nao cole senha em chat, arquivo, historico de comando ou variavel de ambiente.

## 3. Verificar Ambiente

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality
ps -p 1 -o comm=
systemctl is-system-running
cat /etc/os-release
whoami
groups
```

Esperado:

- PID 1: `systemd`
- Ubuntu 24.04/Noble
- usuario no grupo `docker` apos instalacao

## 4. Detectar Dependencia Docker Desktop

```bash
command -v docker || true
command -v docker.exe || true
ls -l /usr/bin/docker /usr/bin/docker-compose 2>/dev/null || true
find /usr/local/lib/docker/cli-plugins -maxdepth 1 -type l -printf '%p -> %l\n' 2>/dev/null || true
docker info 2>/dev/null | grep -Ei 'Operating System|Name:|Docker Root Dir|Server Version|com.docker.desktop' || true
docker context ls 2>/dev/null || true
```

Se aparecer:

- `/mnt/wsl/docker-desktop`
- `Operating System: Docker Desktop`
- `Name: docker-desktop`
- `docker.exe`

entao a distro ainda depende de Docker Desktop.

Se apenas plugins locais residuais em `/usr/local/lib/docker/cli-plugins` apontarem para `/mnt/wsl/docker-desktop`, remova somente esses symlinks verificados em uma boundary operacional. Nao remova o destino `/mnt/wsl/docker-desktop`.

## 5. Instalar Repositorio Oficial Docker Apt

Execute com `sudo` interativo dentro do WSL:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
. /etc/os-release
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

Se `apt-get update` falhar, pare e corrija o erro antes de instalar pacotes.

## 6. Instalar Docker Engine e Compose Plugin

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Validar:

```bash
which docker
docker --version
docker compose version
which dockerd || true
which containerd || true
```

O `which docker` deve apontar para caminho Linux local. Se ainda apontar para `/mnt/wsl/docker-desktop`, a integracao Docker Desktop ainda esta sobrescrevendo binarios.

## 7. Ativar Servico Docker

Com systemd:

```bash
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager --lines=80
```

Fallback, apenas se systemd nao estiver disponivel:

```bash
sudo service docker start
sudo service docker status
```

Nao criar servico permanente improvisado sem documentar.

## 8. Grupo Docker

```bash
getent group docker || sudo groupadd docker
sudo usermod -aG docker "$USER"
```

Depois:

1. Feche a sessao WSL.
2. Abra novamente.
3. Valide:

```bash
groups
docker info
```

Nao usar:

```bash
sudo chmod 666 /var/run/docker.sock
```

## 9. Validar Docker Nativo

```bash
which docker
docker version
docker info
docker compose version
docker run --rm hello-world
docker info | grep -Ei 'Operating System|Docker Root Dir|Server Version|Storage Driver|Name:'
docker context ls
```

Esperado:

- `docker` nao aponta para `/mnt/c` nem `/mnt/wsl/docker-desktop`;
- `Operating System` nao e `Docker Desktop`;
- `Docker Root Dir` e Linux/WSL, normalmente `/var/lib/docker`;
- `hello-world` roda.

## 10. Subir Dependencias do Projeto

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality
docker compose config --services
docker compose up -d postgres redis
docker compose ps
ss -ltnp | egrep ':5432|:6379' || true
```

Se falhar, coletar logs sem secrets:

```bash
docker compose logs --tail=120 postgres redis
```

Nao executar:

```bash
docker compose down -v
```

## 11. Subir Backend

Se porta `8000` ja estiver ocupada:

```bash
ss -ltnp | grep ':8000' || true
curl -i --max-time 10 http://127.0.0.1:8000/health || true
```

Se backend nao estiver ativo:

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality
PYTHONPATH=backend .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Validar:

```bash
curl -i --max-time 10 http://127.0.0.1:8000/health
curl -i --max-time 10 http://127.0.0.1:8000/api/v1/auth/refresh || true
```

`auth/refresh` sem sessao pode responder erro controlado; nao deve travar.

## 12. Subir Frontend Preview

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality/frontend/itam-platform
source "$HOME/.nvm/nvm.sh"
nvm use 22.22.3
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
```

Validar rotas:

```bash
python3 - <<'PY'
from urllib.request import urlopen
ports = [4173, 4174, 4175]
routes = ["/login", "/", "/imports", "/macros", "/ai-chat", "/audit-logs", "/settings", "/assinaturas/", "/admin/"]
for port in ports:
    base = f"http://127.0.0.1:{port}"
    try:
        with urlopen(base + "/login", timeout=5) as r:
            print("BASE", base, r.status)
            for route in routes:
                try:
                    with urlopen(base + route, timeout=5) as rr:
                        print(route, rr.status, rr.geturl())
                except Exception as exc:
                    print(route, "ERROR", type(exc).__name__, exc)
            break
    except Exception:
        pass
PY
```

## 13. Parar Servicos do Projeto

Para parar apenas Postgres/Redis sem apagar volumes:

```bash
cd /home/estevaoqualityadm/projects/Painel-ENS-Quality
docker compose stop postgres redis
```

Para ver status:

```bash
docker compose ps
```

## 14. Diagnosticar Portas

```bash
ss -ltnp | egrep ':5432|:6379|:8000|:4173|:4174|:4175' || true
```

## 15. Comandos Proibidos

Nao executar sem autorizacao explicita:

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

## 16. Quando Abrir Boundary Separada

Abra uma boundary propria para:

- migrar volumes do Docker Desktop para Docker Engine nativo;
- remover Docker Desktop/Windows;
- remover contexto `desktop-linux` ou desativar integracao WSL do Docker Desktop no Windows;
- alterar portas ou compose do projeto;
- mexer em `.env`;
- alterar backend, frontend, migrations ou dependencias.
