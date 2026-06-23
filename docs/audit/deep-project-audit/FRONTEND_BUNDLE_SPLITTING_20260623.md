# Frontend Bundle Splitting - 2026-06-23

## 1. Objetivo
Reduzir warning de bundle grande do Vite com lazy loading de rotas pesadas.

## 2. Antes
- JS principal: `603.21 kB` (`gzip: 174.58 kB`)
- gzip: `174.58 kB`
- warning: `Some chunks are larger than 500 kB after minification.`

## 3. Depois
- JS principal: `289.01 kB` (`gzip: 91.55 kB`)
- gzip: `91.55 kB`
- chunks criados: `AppShell`, `ApoemaApp`, `AiChatPage`, `AssetsPage`, `ImportsPage`, `MacrosPage`, `AuditLogsPage`, `DashboardPage`, `UsersPage`, `SignaturesPage`, `SettingsPage`, `AssignmentsPage`, `AssetDetailsPage`, `StockPage`, `UserDetailsPage`, `LoginPage`, `NotFoundPage`
- warning: removido

## 4. Alterações
- Rotas lazy-loaded: `ApoemaApp`, `AiChatPage`, `AppShell`, `AssetsPage`, `ImportsPage`, `MacrosPage`, `AuditLogsPage`, `DashboardPage`, `UsersPage`, `SignaturesPage`, `SettingsPage`, `AssignmentsPage`, `AssetDetailsPage`, `StockPage`, `UserDetailsPage`, `LoginPage`, `NotFoundPage`
- Loading state: `RouteLoading` com `LoadingBlock` reutilizado

## 5. Validações
- unittest: `PASS`
- ruff: `PASS`
- compileall: `PASS`
- npm run build: `PASS`
- git diff --check: `PASS`

## 6. Riscos
- Suspense adiciona um estado transitório de loading durante a primeira navegação para cada rota lazy-loaded.
- O comportamento funcional das rotas e do `ProtectedRoute` foi preservado.

## 7. Limitações
- A medição foi feita com build local; não houve smoke HTTP do dev server.

## 8. Próxima fase
- Se for necessário reduzir mais, a próxima alavanca segura é dividir submódulos pesados do `AssetsPage` e do `AiChatPage`.
