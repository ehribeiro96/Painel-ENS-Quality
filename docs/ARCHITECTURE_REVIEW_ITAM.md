# Revisao Arquitetural ITAM

Data: 2026-05-15

## Escopo

Esta revisao cobre a plataforma em `backend/` e `frontend/itam-platform/`. O legado de assinaturas em `src/`, `assets/` e `frontend/app` permanece preservado e agora e montado no FastAPI principal em `/assinaturas/` e `/admin/`.

## Diagnostico Executivo

A fundacao modular esta correta para uma Fase 1: dominios separados, FastAPI com SQLAlchemy async, DTOs Pydantic, Alembic, RBAC preparado e frontend integrado como build estatico. Os pontos que exigiam reforco antes de novas features eram auditoria, atomicidade de movimentacao, imutabilidade do historico, consistencia operacional da UI e simplificacao do runtime.

## Riscos Identificados

| Severidade | Area | Risco | Tratamento |
| --- | --- | --- | --- |
| Critico | Movimentacao | Alterar snapshot atual do ativo sem lock poderia gerar corrida operacional em movimentacoes simultaneas. | Adicionado `SELECT FOR UPDATE` no caminho de movimentacao. |
| Critico | Auditoria | Logs nao carregavam `request_id`, `correlation_id`, IP e origem de forma padronizada. | Criado `AuditContext` reutilizavel e middleware injeta IDs na request. |
| Alto | Historico | `AssetMovement` podia ser alterado por codigo futuro, quebrando append-only. | Adicionados listeners SQLAlchemy bloqueando update/delete de movimentos. |
| Alto | Transacoes | Rotas faziam commit direto sem rollback explicito em falhas. | Criado helper `commit_or_rollback` para escritas criticas. |
| Medio | Banco | Indices insuficientes para timeline e consultas de auditoria. | Adicionados indices compostos para movimento e auditoria. |
| Medio | Frontend | Fluxos operacionais principais ainda estavam difusos no console inicial. | Console migrado para React/Vite com rotas protegidas, barra de acoes operacionais e consumo relativo da API. |
| Medio | Operacao | Next.js, backend e NGINX exigiam multiplos processos e CORS para um sistema interno sem SSR real. | Adotado monolito modular integrado: FastAPI serve API, SPA Vite e legado em uma porta. |
| Medio | Dependencias | Pins iniciais nao instalavam corretamente no Python 3.14 local. | Atualizados pins de `pandas`, `pydantic`, `greenlet`, `asyncpg` e `SQLAlchemy` dentro das linhas compativeis. |
| Medio | Seguranca | Upload de inventario nao tinha limite aplicado no service. | Adicionado limite por `UPLOAD_MAX_MB`. |
| Medio | Seguranca | Secret JWT padrao poderia vazar para producao por erro humano. | Configuracao agora falha em `production` se o secret padrao for usado. |
| Baixo | Documentacao | Decisoes arquiteturais ainda estavam implicitas. | Documentada esta revisao e atualizado README. |

## Decisoes Arquiteturais

1. Movimentacao e o caso de uso central.
   - A operacao deve travar o ativo, registrar movimento append-only, atualizar snapshot atual e gravar auditoria na mesma transacao.

2. Auditoria deve ser desacoplada.
   - Services recebem `AuditContext` opcional, evitando acoplamento direto com FastAPI e mantendo reuso futuro por jobs/filas.

3. O historico e imutavel por padrao.
   - `AssetMovement` nao deve ser atualizado ou removido pela aplicacao. Correcoes futuras devem ser registradas como novos eventos compensatorios.

4. Frontend deve priorizar operacao, nao apresentacao.
   - A primeira tela deve favorecer localizar ativo, movimentar, enviar para estoque, consultar historico e importar inventario.

5. Runtime deve ser simples.
   - O console enterprise e build estatico Vite servido pelo FastAPI. Next.js foi removido porque nao havia uso real de SSR, SEO, edge rendering ou server actions.

## Pendencias Intencionais

- Repository Pattern ainda nao foi extraido porque os services estao pequenos. Extrair agora geraria cerimonia prematura.
- Multi-tenant nao foi implementado. A modelagem deve reservar esse debate para antes de onboarding multiempresa.
- pgvector e busca semantica ficam no roadmap; neste momento indices relacionais e busca textual simples sao suficientes.
- Fluxos avancados de cadastro/edicao no frontend ainda devem ser tratados por iteracoes de produto; a integracao atual preserva rotas, listagens e operacao base.

## Proximos Passos Tecnicos

1. Adicionar testes de contrato para `POST /assets/{id}/move`.
2. Criar seed seguro de usuario ADMIN local via comando operacional.
3. Expandir os formularios operacionais do frontend sobre a API ja integrada.
4. Definir politica formal de eventos compensatorios para correcao de movimentacoes.
5. Adicionar limites de tamanho e streaming para importacoes grandes.
