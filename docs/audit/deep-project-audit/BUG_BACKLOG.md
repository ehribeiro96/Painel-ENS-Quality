# Bug Backlog — Deep Project Audit 2026-06-23

## P0_BLOCKER

_Nenhum P0 confirmado por gates automatizados e análise estática pós-commit `283d9bc`._

## P1_HIGH

### BUG-001 — Apoema Chat mascara falha de API/sessão com resposta mock
- Severidade: P1_HIGH
- Área: Apoema / AI Chat
- Rota/endpoint: `/apoema/chat`, `POST /api/v1/ai-chat/message`
- Passos: Autenticar → abrir Apoema Chat → expirar sessão ou derrubar backend → enviar mensagem
- Esperado: Erro claro de sessão expirada ou indisponibilidade do backend
- Atual: `sendAiMessage` captura qualquer erro e retorna resposta mock com `status: "offline"`, simulando sucesso conversacional
- Evidência: `frontend/itam-platform/src/apoema/lib/apoemaChatApi.ts` linhas 86–115; testes não cobrem UX de 401
- Arquivos prováveis: `apoemaChatApi.ts`, `apoema/pages/ChatPage.tsx`
- Recomendação: Propagar `401/403` para UI; reservar mock apenas quando backend explicitamente indisponível em modo preview dev
- Risco de regressão: médio

### BUG-002 — Lista de providers Apoema oculta falha de autenticação
- Severidade: P1_HIGH
- Área: Apoema / AI Chat
- Rota/endpoint: `GET /api/v1/ai-chat/providers`
- Passos: Abrir chat Apoema com token inválido ou backend retornando 401
- Esperado: Aviso de sessão expirada ou erro de permissão
- Atual: `getAiProviders` faz `catch` e retorna `DEFAULT_PROVIDER_OPTIONS`; UI mostra providers como se estivessem online
- Evidência: `apoemaChatApi.ts` linhas 77–83; `ChatPage.tsx` linhas 115–121
- Arquivos prováveis: `apoemaChatApi.ts`, `ChatPage.tsx`
- Recomendação: Diferenciar erro de auth (401/403) de erro de rede; não substituir por catálogo mock silenciosamente
- Risco de regressão: baixo

### BUG-003 — Auditoria autenticada de fluxos principais não executada
- Severidade: P1_HIGH (limitação de auditoria com impacto em confiança do GO)
- Área: QA / Runtime
- Rota/endpoint: Todas as rotas protegidas
- Passos: Executar `npm run uat:ui:smoke` ou Playwright autenticado
- Esperado: Smoke autenticado com credencial segura
- Atual: `uat:ui:smoke` retornou `NO-GO_UAT_CREDENTIAL_UNAVAILABLE`; backend WSL bridge indisponível
- Evidência: `deep-audit-gates.log`, `deep-audit-runtime.log`
- Arquivos prováveis: `scripts/ui-auth-smoke.cjs`
- Recomendação: Repetir auditoria com backend ativo + credencial em arquivo temporário fora do repo
- Risco de regressão: n/a (auditoria)

## P2_MEDIUM

### BUG-004 — Busca global engole erros de API
- Severidade: P2_MEDIUM
- Área: UX / Shell
- Rota/tela: Todas (topbar)
- Passos: Autenticar → buscar com backend/API indisponível
- Esperado: Feedback de erro ou sessão expirada
- Atual: `.catch(() => setResults([]))` exibe "Nenhum resultado"
- Evidência: `AppShell.tsx` linha 66
- Arquivos prováveis: `AppShell.tsx`
- Recomendação: Mapear 401/403/5xx para alerta visível
- Risco de regressão: baixo

### BUG-005 — Apoema Assets/Integrations usam dados mock sem distinção forte
- Severidade: P2_MEDIUM
- Área: Apoema UX
- Rota/tela: `/apoema/assets`, `/apoema/integrations`
- Passos: Abrir rotas Apoema autenticado
- Esperado: Indicação explícita de dados simulados vs inventário real
- Atual: Páginas consomem `apoema/data.ts` estático; rótulo "Preview" existe no shell mas dados parecem operacionais
- Evidência: `apoema/pages/AssetsPage.tsx`, `apoema/data.ts`
- Arquivos prováveis: páginas Apoema
- Recomendação: Banner persistente "dados de demonstração" em todas as telas mock
- Risco de regressão: baixo

### BUG-006 — Mensagens PT-BR sem acentuação em fluxos críticos
- Severidade: P2_MEDIUM
- Área: UX / i18n
- Rota/tela: `/login`, `/` (guards), `/stock`, `/users/:id`
- Passos: Abrir telas ou acionar erro
- Esperado: Português correto ("não", "sessão", "inválidas")
- Atual: "Validando sessao", "Credenciais invalidas", "Acesso nao autorizado", "Nao foi possivel..."
- Evidência: `LoginPage.tsx`, `App.tsx`, `StockPage.tsx`, `UserDetailsPage.tsx`
- Arquivos prováveis: múltiplas pages
- Recomendação: Normalizar cópias PT-BR
- Risco de regressão: baixo

### BUG-007 — Rate limit HTTP da API permanece em memória por processo
- Severidade: P2_MEDIUM
- Área: Segurança / Backend
- Rota/endpoint: `/api/v1/*`
- Passos: Escalar app com múltiplos workers
- Esperado: Rate limit consistente entre instâncias
- Atual: `_rate_limit_buckets` em `main.py` é local ao processo
- Evidência: `backend/app/main.py` linhas 26, 77–89
- Arquivos prováveis: `main.py`
- Recomendação: Redis-backed rate limit (AI chat já tem abstração)
- Risco de regressão: médio

### BUG-008 — Settings do painel principal é puramente visual
- Severidade: P2_MEDIUM
- Área: UX
- Rota/tela: `/settings`
- Passos: ADMIN acessa configurações e interage com seções
- Esperado: Persistência ou rótulo inequívoco de mockup
- Atual: Badge "Somente visual" existe, mas seções descrevem integrações/segurança como se fossem configuráveis
- Evidência: `SettingsPage.tsx`
- Arquivos prováveis: `SettingsPage.tsx`
- Recomendação: Desabilitar controles ou conectar a endpoints reais
- Risco de regressão: baixo

### BUG-009 — Topbar exibe status "Online" estático
- Severidade: P2_MEDIUM
- Área: UX
- Rota/tela: Shell autenticado
- Passos: Derrubar backend com SPA aberta
- Esperado: Indicador reflete saúde real
- Atual: `HermesStatusPill state="Online"` fixo
- Evidência: `AppShell.tsx` linhas 141–142
- Arquivos prováveis: `AppShell.tsx`, `HermesStatusPill`
- Recomendação: Consultar `/health/ready` periodicamente
- Risco de regressão: baixo

### BUG-010 — Sem scripts `lint`/`test` no frontend
- Severidade: P2_MEDIUM
- Área: Qualidade / CI
- Rota/endpoint: n/a
- Passos: `npm run lint` / `npm run test`
- Esperado: Scripts disponíveis no CI
- Atual: Apenas `dev`, `build`, `preview`, `uat:ui:smoke`
- Evidência: `package.json`, `deep-audit-gates.log`
- Arquivos prováveis: `package.json`, CI workflow
- Recomendação: Adicionar ESLint + testes mínimos de rota
- Risco de regressão: baixo

### BUG-011 — Bundle JS acima de 500 KB sem code-splitting
- Severidade: P2_MEDIUM
- Área: Performance
- Rota/tela: Todas
- Passos: `npm run build`
- Esperado: Chunks menores ou lazy routes
- Atual: Vite warning `index-*.js` ~599 KB
- Evidência: `deep-audit-gates.log`
- Arquivos prováveis: `vite.config.ts`, rotas React
- Recomendação: `React.lazy` para Apoema, AiChat, Imports
- Risco de regressão: médio

## P3_LOW

### BUG-012 — `enableAiChat` definido mas não consumido
- Severidade: P3_LOW
- Área: Frontend
- Rota/tela: Menu IA
- Passos: Buscar uso de `enableAiChat`
- Esperado: Menu IA condicionado à flag
- Atual: Export em `features.ts` sem referências
- Evidência: grep em `frontend/itam-platform/src`
- Arquivos prováveis: `features.ts`, `AppShell.tsx`
- Recomendação: Usar flag ou remover dead code
- Risco de regressão: baixo

### BUG-013 — Diálogos `window.confirm` para ações destrutivas
- Severidade: P3_LOW
- Área: Acessibilidade
- Rota/tela: Assets, Users, Imports
- Passos: Excluir ativo / desativar usuário / aplicar importação
- Esperado: Modal acessível com foco gerenciado
- Atual: `window.confirm` nativo
- Evidência: `AssetsPage.tsx`, `UsersPage.tsx`, `ImportsPage.tsx`
- Recomendação: Componente modal acessível
- Risco de regressão: baixo

### BUG-014 — Link legado de assinaturas sem contexto RBAC
- Severidade: P3_LOW
- Área: UX / Legado
- Rota/tela: Sidebar footer
- Passos: Clicar "Assinaturas legado"
- Esperado: Transição clara para app Flask separado
- Atual: Link `<a href="/assinaturas/">` abre stack legada com auth própria
- Evidência: `AppShell.tsx` linha 110
- Arquivos prováveis: `AppShell.tsx`
- Recomendação: Tooltip/modal explicando autenticação legada
- Risco de regressão: baixo

## INFO

### INFO-001 — Hardening P0/P1 aplicado em `283d9bc`
- Apoema em `ProtectedRoute`, AI endpoints com RBAC, metrics com token fora de local, docker compose com bind localhost, `APP_AUTO_MIGRATE=0` no compose

### INFO-002 — JWT default permitido apenas em `environment=local`
- `settings.py` rejeita secret fraco em staging/production via `_is_weak_jwt_secret`

### INFO-003 — Upload frontend alinhado ao backend (.csv, .xlsx)
- `ImportsPage.tsx` accept corrigido

### INFO-004 — Vite proxy aponta para porta 8080 (alinhado ao runtime)
- `vite.config.ts`

### INFO-005 — 172 testes unittest OK (8 skipped por credencial/operacional)
