# Phase 7.1C Native Docker Migration Plan Report

## Resumo executivo

Esta fase transformou a auditoria do Docker Desktop WSL em um plano executável e auditável para futura migração ao Docker Engine nativo, sem alterar o runtime atual.

## Status final

`GO COM RESSALVAS - plano de migracao nativa pronto, sem execucao`

## Confirmação de runtime

- nenhum `up`, `down`, `stop`, `restart` ou troca de context foi executado
- `.env.hml` nao foi alterado

## Runtime atual

`Docker Desktop WSL integration`

## Containers atuais

- `hermesops_hml_postgres`
- `hermesops_hml_redis`
- `hermesops_hml_qdrant`

## Dados a migrar

- PostgreSQL: persistência crítica
- Qdrant: persistência crítica se houver collections
- Redis: depende da política de uso
- network e containers: recriáveis

## Plano de backup lógico

Documentado em `04_LOGICAL_BACKUP_PLAN.md`.

## Plano de instalação futura

Documentado em `05_NATIVE_ENGINE_INSTALLATION_PLAN.md`.

## Estratégia de contexts

Documentada em `06_DOCKER_CONTEXT_STRATEGY.md`.

## Plano de cutover

Documentado em `07_NATIVE_ENGINE_CUTOVER_PLAN.md`.

## Matriz de riscos

Documentada em `08_NATIVE_DOCKER_MIGRATION_RISK_REGISTER.md`.

## Checklist de aprovação humana

Documentado em `09_HUMAN_APPROVAL_CHECKLIST_NATIVE_DOCKER.md`.

## Scan de segurança

- sem segredos nos relatórios
- sem arquivos proibidos nos relatórios

## Decisão recomendada

Preparar a migração para Docker Engine nativo, mas manter Docker Desktop no curto prazo até haver janela de manutenção e backup lógico validado.

## Próxima fase recomendada

Uma fase de preparação operacional com aprovação humana explícita para o backup lógico e definição do daemon alvo, sem qualquer troca de runtime ainda.
