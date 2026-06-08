# Plano Futuro - Instalação Docker Engine Nativo no WSL/Linux

## Status

Plano documental. Nenhuma instalação foi executada nesta fase.

## Pré-condições

- Janela de manutenção aprovada.
- Backup lógico concluído.
- Contexto Docker atual documentado.
- Containers atuais preservados.
- Decisão de cutover aprovada.
- Política de rollback aprovada.

## Instalação futura

Seguir documentação oficial Docker Engine para Ubuntu/Debian conforme distro real.

Comandos futuros devem ser revisados antes da execução.

## Regras

- Não misturar Docker Desktop e Docker Engine nativo sem contexts claros.
- Não usar `docker context use` sem aprovação.
- Não subir o mesmo Compose em dois daemons ao mesmo tempo usando as mesmas portas.
- Não copiar volumes brutos como estratégia primária.
- Não executar `down -v`.

## Validação futura

- `docker context ls`
- `docker context show`
- `docker version`
- `docker info`
- `docker compose version`
- `docker compose config`
