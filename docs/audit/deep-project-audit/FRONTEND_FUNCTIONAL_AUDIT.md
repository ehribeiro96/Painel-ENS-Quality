# Frontend Functional Audit — Deep Project Audit 2026-06-23

## Limitações desta execução

- Backend WSL (`172.18.0.1:8080`): **indisponível**
- Credencial UAT: **ausente** (`/tmp/painel_runtime_h5_credentials.txt`)
- Playwright route audit: **SKIPPED** (binários Chromium não instalados)
- Frontend dev (`127.0.0.1:18086`): **HTTP 200** confirmado
- Auditoria autenticada: **limitada** — análise estática + redirect logic + código

## Resultado por rota (não autenticado)

| Rota | Redirect esperado | Evidência estática | Console/network |
|------|-------------------|--------------------|---------------|
| `/login` | Público | `LoginPage` renderiza form | Não medido (Playwright skip) |
| `/` | → `/login` | `ProtectedRoute` + `ShellRoute` | Inferência: redirect |
| `/assets` | → `/login` | `ProtectedRoute` | Inferência: redirect |
| `/users` | → `/login` | idem | idem |
| `/assignments` | → `/login` | idem | idem |
| `/stock` | → `/login` | idem | idem |
| `/signatures` | → `/login` | idem | idem |
| `/ai-chat` | → `/login` | idem | idem |
| `/imports` | → `/login` | `RoleGuard` após auth | idem |
| `/macros` | → `/login` | idem | idem |
| `/audit-logs` | → `/login` | idem | idem |
| `/settings` | → `/login` | idem | idem |
| `/apoema` | → `/login` | `ProtectedRoute` + `ApoemaApp` | idem |
| `/apoema-preview` | → `/login` | idem | idem |
| `/apoema-preview/chat` | → `/login` | rota interna `chat` | idem |

## Resultado por módulo (código + padrões UX)

### Login/Auth
- Form com loading/erro: **OK**
- Mensagens sem acento: **BUG-006**
- Token não logado no console: **OK** (sem `console.log` de token)
- Refresh automático via cookie: **OK** (`auth.tsx`)

### Dashboard
- React Query + loading/error: **OK** (`DashboardPage.tsx`)
- Empty states via `Base44EmptyState`: **OK**
- Responsividade: grids com `auto-fit minmax` — **OK** estático

### Ativos
- Filtros, paginação, CRUD condicionado a `canWrite`: **OK**
- Empty/error/loading: **OK**
- Página grande (564 linhas): manutenibilidade **P3**

### Movimentações / Assignments / Stock
- Carregam via API com estados de erro genéricos
- Stock: mensagem sem acento — **BUG-006**

### Importações
- Accept `.csv,.xlsx`: **OK** (pós-hardening)
- Fluxo upload → preview → apply com confirmações: **OK**
- Erros genéricos em catch — **P3**

### Macros ITIL
- Listagem, render, copy, autocomplete: implementados
- Permissão UI + backend alinhadas para ADMIN/TECH

### Chat IA principal
- Rota protegida, composer, presets, anexos: **OK**
- `mapAiChatError` para 401/403/502/503: **OK**
- Não chama Ollama direto: **OK**

### Apoema
- ProtectedRoute: **OK**
- Chat usa backend com token: **OK**
- Fallback mock em erro: **BUG-001/002**
- Tema claro/escuro/auto: **OK** (`useThemeMode`)
- Assets/Integrations mock: **BUG-005**
- CSS responsivo em `apoema.css` com breakpoints — **OK** estático

### Usuários/RBAC
- Menu filtrado: **OK**
- Ações de escrita ocultas para VIEWER: **OK**

### Assinaturas
- Lista colaboradores reais via API
- Preview/download HTML
- Link legado na sidebar — **BUG-014**

### Audit logs
- Role ADMIN/MANAGER
- Paginação e filtros presentes

### Settings
- Cosmético — **BUG-008**

## Responsividade (análise CSS)

- `styles.css`: breakpoints 1200, 900, 760px — shell colapsa sidebar
- `apoema.css`: breakpoints 1180, 820px
- Sem auditoria visual pixel-perfect (screenshots não gerados)

## Scripts frontend

```json
{
  "dev": "vite",
  "build": "tsc --noEmit && vite build",
  "preview": "vite preview",
  "uat:ui:smoke": "node scripts/ui-auth-smoke.cjs"
}
```

`uat:ui:smoke` → `NO-GO_UAT_CREDENTIAL_UNAVAILABLE`
