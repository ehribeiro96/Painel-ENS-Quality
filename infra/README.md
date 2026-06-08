# Infraestrutura

O runtime oficial atual usa `docker-compose.yml` com os servicos `postgres`,
`redis` e `app`. O frontend Vite e buildado e servido pelo proprio FastAPI.

`infra/nginx/nginx.conf` e uma configuracao opcional de proxy reverso para esse
modelo integrado. Ela aponta para `app:8080` e nao deve ser confundida com a
arquitetura antiga de backend e frontend separados.
