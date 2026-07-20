# Segurança do Apoema — Hardening Fase 1

## Escopo

Esta referência consolida a arquitetura de autorização da IA, RBAC, autenticação e riscos conhecidos. Ela não substitui os documentos funcionais de cada domínio e não habilita novas funcionalidades.

## Arquitetura Hermes e fluxo de IA

Fluxo obrigatório no backend:

1. usuário autenticado por JWT;
2. papel resolvido a partir do usuário canônico no PostgreSQL;
3. `require_ai_capability` avalia uma capability explícita;
4. `ensure_ai_enabled` aplica `ENABLE_AI_CHAT` antes de qualquer catálogo, health ou geração;
5. somente então o endpoint chama o provider;
6. autorização e resultado HTTP são registrados em logs estruturados, sem prompt, token ou chave.

O frontend nunca chama Hermes, Ollama, Gemini ou OpenAI diretamente. O `HermesTerminalProvider` permanece uma implementação interna e só é alcançável por rotas protegidas. A IA continua textual: não há tool calling nem mutação operacional automática.
O subprocesso Hermes usa somente o toolset não operacional `todo`, ignora regras/memórias carregadas do ambiente, limita a execução a um turno e nunca usa `--yolo`; toolsets de terminal, arquivos, código, browser, cron e memória não são expostos ao modelo do Apoema.

## Capabilities de IA

| Capability | ADMIN | TECHNICIAN | MANAGER | VIEWER |
|---|---:|---:|---:|---:|
| `AI_CHAT_ACCESS` | sim | sim | sim | não |
| `AI_MACRO_GENERATION` | sim | sim | não | não |
| `AI_IMPORT_ANALYSIS` | sim | sim | não | não |
| `AI_PROVIDER_CONFIGURATION` | sim | não | não | não |

`VIEWER` pode consultar superfícies operacionais permitidas pelo RBAC geral, mas não pode listar providers, disparar health de provider ou gerar conteúdo por IA.

## RBAC geral

| Domínio | ADMIN | TECHNICIAN | VIEWER |
|---|---|---|---|
| usuários, papéis e privilégios | administrar | somente consultar | somente consultar |
| assets, tickets e operações autorizadas | administrar | operar conforme rotas existentes | consultar |
| configuração de IA | autorizado por capability | negado | negado |

Criação, atualização e exclusão de usuários exigem `ADMIN`. O bloqueio inclui alteração de administradores, elevação de terceiros e autoelevação por técnicos.

## Feature flag

Com `ENABLE_AI_CHAT=false`, as rotas de mensagem, providers, health de IA, geração ITIL e análise de import retornam `403 ai_chat_disabled` antes de banco ou provider. O health de IA não executa Hermes quando desabilitado.
O ambiente local mantém IA ligada por padrão, mas agora respeita `ENABLE_AI_CHAT=false` explícito em vez de sobrescrever a decisão operacional.

## Health seguro

- `/health` e `/health/live`: somente `{ "status": "ok" }`.
- `/health/ready` e o alias compatível `/health/dependencies`: somente os booleanos `database`, `redis` e `migrations`, com HTTP 503 quando algum estiver falso.
- detalhes de exceção, SQL, tabelas, revisões Alembic, URLs e estado de bootstrap não são retornados ao cliente.

## Autenticação e sessão

Estado atual:

- refresh token: cookie `HttpOnly`, `SameSite` configurável, `Secure` conforme ambiente, rotação no refresh e revogação no logout;
- access token: retornado no corpo e persistido em `localStorage` pelo frontend;
- refresh inicial: usa `AbortSignal`, timeout e neutraliza `AbortError` durante cleanup do React StrictMode;
- logout: aguarda a revogação/limpeza da sessão antes de navegar para `/login`, evitando redirecionamento de volta com token ainda presente;
- expiração e reload: o frontend tenta refresh pelo cookie e limpa sessão em 401/403 reais.

### REQUIRES_ARCHITECTURE_DECISION: access token em cookie HttpOnly

A migração completa não foi feita nesta fase porque exige decisão conjunta sobre autenticação cookie-first, proteção CSRF, compatibilidade com clientes Bearer, CORS, rollout e rollback. Alterar apenas o armazenamento frontend deixaria o backend incompatível. Próxima decisão recomendada:

1. aceitar access cookie em paralelo ao Bearer;
2. adicionar CSRF para métodos mutáveis;
3. migrar o frontend sem `localStorage`;
4. observar e remover Bearer somente após janela de compatibilidade.

## Macros

Uma constraint/índice único parcial protege `asset_movement` por `context_id`. O serviço usa savepoint e, em corrida, retorna a geração vencedora. A migration não remove duplicatas existentes: antes de aplicá-la, o operador deve consultar duplicidades e decidir correção manual auditada. Nenhuma migration foi executada automaticamente.

## Imports e IA

O fluxo permanece staging-first:

`upload -> normalização determinística -> sugestão IA -> revisão humana -> apply existente`

Sugestões Hermes são DTOs de resposta, exigem `requires_review=true` e não são gravadas/aplicadas automaticamente. Campos críticos (`serial`, `patrimony`, `ip_address`, `mac_address`, `user`, `location`) sem valor-fonte real são rejeitados mesmo se o provider alegar um `original_value`.

## Auditoria

A autorização de IA registra em log estruturado:

- `user_id`;
- capability em `action`;
- timestamp UTC;
- `allowed` ou `denied` em `result`.

O middleware registra o status HTTP final com request/correlation ID. Operações persistentes existentes continuam usando `AuditService`.

## Riscos conhecidos

1. `REQUIRES_ARCHITECTURE_DECISION`: access token ainda em `localStorage`, sujeito a exfiltração em caso de XSS.
2. A migration de idempotência precisa de precheck de duplicatas e janela controlada antes de execução.
3. Health interno detalhado continua existindo como função Python para diagnóstico, mas não é exposto por rota pública.
4. Logs estruturados de autorização dependem da retenção e proteção do pipeline de logs; persistência dedicada de eventos de autorização pode ser avaliada depois, sem bloquear o P0.
5. Testes operacionais dependentes de runtime/credenciais continuam explicitamente condicionais; a CI executa uma suíte crítica determinística separada, sem skips.
6. `npm audit` ainda reporta uma vulnerabilidade baixa transitiva em `@babel/core`; o achado alto direto do Vite foi removido com a atualização compatível para 6.4.3.
7. O catálogo de providers ainda faz probe ativo do Hermes quando a IA está habilitada; separar catálogo estático de diagnóstico ativo fica para uma fase operacional posterior.
8. `X-Forwarded-For` e `X-Audit-Source` dependem de normalização por proxy confiável; a política de proxy/CIDR requer decisão de arquitetura.
9. O caminho Hermes candidato a produção opera em modo fail-closed: falhas e timeouts retornam erro controlado e auditado, sem fallback mock automático. O provider mock permanece apenas para uso explícito em ambiente de teste ou desenvolvimento.
