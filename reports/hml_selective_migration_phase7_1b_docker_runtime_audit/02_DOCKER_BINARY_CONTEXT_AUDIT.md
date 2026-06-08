# Docker Binary and Context Audit

## Classificacao

`Docker Desktop WSL integration`

## Evidencias principais

- `docker` resolve para o binario do Desktop em `/mnt/wsl/docker-desktop/cli-tools/usr/bin/docker`
- `docker context show` retornou `default`
- `docker context ls` mostra `desktop-linux` como contexto do Docker Desktop
- `docker version` indica `Server: Docker Desktop 4.76.0`
- `docker info` mostra `Operating System: Docker Desktop`

## Conclusao

O CLI esta integrado ao Docker Desktop, operando via contexto `default` e socket local do Desktop exposto no WSL.
