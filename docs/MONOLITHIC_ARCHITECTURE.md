# Arquitetura Monolitica Modular Integrada

Data: 2026-05-22

## Decisao

A plataforma passa a operar como uma aplicacao unica:

```text
python run.py
```

Esse comando prepara o build estatico do frontend quando necessario e inicia o FastAPI enterprise, que serve:

- API REST em `/api/v1`;
- console React/Vite;
- assets estaticos do frontend;
- fallback de rotas SPA;
- legado de assinaturas em `/assinaturas/`;
- administracao legada em `/admin/`.

## Por que Vite

O console atual nao usa SSR, SEO, edge rendering, server actions ou APIs Next. Para um sistema interno operacional, Next.js exigia um runtime Node separado sem ganho funcional claro.

React + Vite preserva TypeScript, componentes e UX, mas entrega um artefato estatico simples para o FastAPI servir. Isso reduz:

- processos;
- portas;
- CORS;
- proxy reverso obrigatorio;
- superficie de deploy;
- pontos de falha em Windows e Docker.

## Fronteiras

O backend continua dono de regras de negocio, autenticacao, RBAC, auditoria, importacao e persistencia.

O frontend e apenas uma camada de interacao compilada para arquivos estaticos. Ele consome a API por caminho relativo, sem conhecer host ou porta do backend.

O legado fica preservado em seu proprio modulo e montado como WSGI. Ele nao foi reescrito e nao bloqueia a evolucao do console enterprise.

## Estrutura Alvo

```text
backend/
  app/
    api/
    core/
    domains/
    integrations/
    shared/
  alembic/
frontend/
  itam-platform/
    src/
    dist/
src/
  legacy/
assets/
docs/
scripts/
run.py
docker-compose.yml
```

## Pipeline

Local:

1. Instalar dependencias Python.
2. Subir PostgreSQL/Redis.
3. Executar Alembic.
4. Rodar `python run.py`.

Docker:

1. Builder Node gera `frontend/itam-platform/dist`.
2. Imagem Python instala backend e dependencias legadas.
3. Runtime executa `python run.py` com `ENS_BUILD_FRONTEND=0`.

## Regras Mantidas

- Sem microservices.
- Sem Kubernetes.
- Sem NGINX obrigatorio.
- Sem proxy para frontend.
- Sem CORS na execucao integrada.
- Sem sobrescrever o legado.
- Sem mover regras de dominio para o frontend.
