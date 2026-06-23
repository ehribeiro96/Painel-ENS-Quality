# Apoema Hermes Redesign — 2026-06-23

## 1. Status
GO

## 2. Objetivo
Redesenhar o visual do Apoema para uma leitura mais próxima de um desktop app Hermes/Electron: escuro, sólido, compacto e com menos ruído visual.

## 3. O que mudou
- Troquei o tema padrão do Apoema para `dark`.
- Repliquei a direção visual do Hermes Desktop com superfícies escuras, bordas sutis e layout mais denso.
- Ajustei a shell do Apoema para parecer mais nativa e menos com cara de dashboard web genérico.
- Reforcei o contraste e a tipografia dos estados de chat, dashboard, integrações e ajustes.
- Eliminei labels em inglês que competiam com a identidade operacional do app.

## 4. Arquivos principais
- `frontend/itam-platform/src/apoema/styles/apoema.css`
- `frontend/itam-platform/src/apoema/hooks/useThemeMode.ts`
- `frontend/itam-platform/src/apoema/components/ApoemaLogo.tsx`
- `frontend/itam-platform/src/apoema/ApoemaApp.tsx`
- `frontend/itam-platform/src/apoema/pages/DashboardPage.tsx`
- `frontend/itam-platform/src/apoema/pages/ChatPage.tsx`
- `frontend/itam-platform/src/apoema/pages/SettingsPage.tsx`
- `frontend/itam-platform/src/apoema/pages/IntegrationsPage.tsx`

## 5. Referências
- Relatórios locais do Hermes Desktop/Electron.
- Capturas prévias do Apoema já auditadas.
- Conceitos visuais gerados para dashboard e chat.

## 6. Validação visual
- Capturas antes e depois nas rotas principais.
- Inspeção manual do dashboard e do chat em desktop e mobile.

## 7. Validações técnicas
Ainda será executado o pacote de build, lint e testes após a consolidação final do diff.

## 8. Limitações
- Não havia source local do Hermes Desktop para copiar.
- A direção foi extraída de relatórios, screenshots e do conceito gerado nesta sessão.
