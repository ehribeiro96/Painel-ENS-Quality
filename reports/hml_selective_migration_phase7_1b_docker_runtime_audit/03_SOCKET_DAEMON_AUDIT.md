# Socket and Daemon Audit

## Socket observado

- `/var/run/docker.sock` existe e esta acessivel no ambiente WSL

## Daemon observado

- `docker info` identifica o servidor como `Docker Desktop`
- o host reportado pelo daemon e `docker-desktop`
- o kernel do ambiente e `6.6.114.1-microsoft-standard-WSL2`

## systemd e WSL

- `systemd` esta ativo no WSL (`PID 1 = systemd`)
- `wsl.exe -l -v` mostra `Ubuntu-24.04` como distro ativa e `docker-desktop` como distro de suporte

## Conclusao

O runtime atual depende do Docker Desktop com integracao WSL, nao de um `dockerd` nativo operando como daemon primario neste shell.
