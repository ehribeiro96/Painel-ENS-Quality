Config
------

- `requirements.txt`: copia historica de dependencias do portal legado. Foi movida para `_archive_cleanup_candidates/config_legacy/` na limpeza conservadora; use `requirements.txt` da raiz para o legado ativo.

O Docker principal do projeto agora fica em:

- `backend/Dockerfile`
- `docker-compose.yml`

Nao mantenha um segundo Dockerfile operacional nesta pasta. A execucao suportada e o monolito modular integrado via `python run.py`.
