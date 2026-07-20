# Deployment controlado

Procedimento para promover uma versão aprovada do Painel ENS Quality / Apoema sem recriar PostgreSQL ou Redis.

## Pré-condições

- Pull Request aprovada e checks verdes.
- Tag anotada existente no GitHub.
- Janela de mudança e responsável por rollback definidos.
- Backup do PostgreSQL concluído, íntegro e armazenado fora do repositório.
- Precheck da migration sem duplicidades incompatíveis.
- Variáveis obrigatórias definidas no ambiente, sem registrar valores: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `ADMIN_PASSWORD`, `ENVIRONMENT`, `ENABLE_AI_CHAT`, `AI_CHAT_DEFAULT_PROVIDER` e configuração do provider escolhido.

## Procedimento

1. Registrar versão atual, containers e health.
2. Criar e verificar o backup do PostgreSQL pelo procedimento operacional aprovado. Não imprimir conexão, credenciais nem conteúdo do dump.
3. Executar o precheck somente leitura da migration 0007 com usuário PostgreSQL read-only e preservar a saída como evidência:

   ```bash
   psql "$DATABASE_URL_READ_ONLY" --set ON_ERROR_STOP=1 \
     --file docs/operations/sql/precheck-0007-macro-movement-unique.sql \
     > precheck-0007-macro-movement-unique.txt
   ```

   Zero linhas significa `READY_TO_MIGRATE`. Uma ou mais linhas significa `STOP_DATA_CONFLICT`: não aplicar a migration, não deduplicar automaticamente e encaminhar decisão manual auditada. A migration só pode seguir após precheck vazio e backup verificado.

4. Fazer checkout da tag aprovada:

   ```bash
   git fetch origin --tags
   git switch --detach v1.0.0-rc1
   ```

5. Validar o grafo Alembic e aplicar a migration com o ambiente virtual do projeto:

   ```bash
   cd /home/estevaoqualityadm/projects/Painel-ENS-Quality
   ./.venv/bin/alembic heads
   cd backend
   ../.venv/bin/python -m alembic upgrade head
   cd ..
   ```

6. Construir e recriar somente a aplicação:

   ```bash
   docker compose build app
   docker compose up -d --no-deps --force-recreate app
   ```

7. Confirmar que os IDs e `StartedAt` de PostgreSQL e Redis não mudaram.
8. Confirmar o hash dos arquivos críticos entre host e container.
9. Aguardar o serviço `app` ficar healthy.

## Health checks

```bash
curl --fail --show-error http://localhost:8080/health
curl --fail --show-error http://localhost:8080/health/live
curl --fail --show-error http://localhost:8080/health/ready
```

No WSL/Docker, falha específica de `127.0.0.1:8080` deve ser comparada com localhost/IPv6 e probe interno antes de classificar o app como indisponível.

## Smoke autenticado

- Login, refresh e logout.
- Matriz `ADMIN`/`TECHNICIAN`/`VIEWER`.
- `/login`, `/apoema/dashboard` e proxy `/api/v1`.
- Mensagem Hermes real, sem fallback mock.
- Persistência de auditoria de sucesso e falha de IA.
- Macro ITIL após movimentação salva e cópia pelo histórico.
- Import IA staging-first com sugestão, aprovação e rejeição; confirmar ausência de apply automático.

## Critérios de sucesso

- Alembic no head esperado.
- App healthy e readiness com database, Redis e migrations prontos.
- PostgreSQL e Redis preservados.
- Hash host/container correspondente.
- Smoke autenticado sem regressão.

Qualquer falha nesses critérios interrompe o rollout e aciona [rollback](rollback.md).
