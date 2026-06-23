# Hermes Reference Notes — 2026-06-23

## 1. Local references found
- `docs/hermesops/desktop-cli/reports/DESKTOP_UI_STRUCTURE_AUDIT.md`
- `docs/hermesops/desktop-cli/reports/DARK_MODE_FIX_REPORT.md`
- `docs/hermesops/desktop-cli/reports/HERMES_DESKTOP_SOURCE_DISCOVERY.md`
- `docs/apoema-visual-qa/screenshots/after-polish/1366-dashboard.png`
- `docs/apoema-visual-qa/screenshots/after-polish/1366-chat.png`

## 2. Hermes Desktop source status
- Nenhum source local do Hermes Desktop/Electron foi encontrado no ambiente disponível.
- As referências úteis vieram de relatórios, screenshots e diretrizes já documentadas no repo.

## 3. Design direction extracted
- Shell desktop escuro, sólido e compacto.
- Sidebar com navegação simples e baixa poluição visual.
- Topbar curta, funcional e com controles de tema.
- Painéis com bordas suaves, contraste baixo e hierarquia clara.
- Chat com colunas bem definidas e estados de fallback visíveis.

## 4. Generated concepts used
- `/mnt/c/Users/estevao.quality.adm/.codex/generated_images/019e8f20-ecd6-7f61-93e6-5d428fef64f5/ig_00c0a8afbafc1ecf016a3b0a0d01dc8191a98838db76633126.png`
- `/mnt/c/Users/estevao.quality.adm/.codex/generated_images/019e8f20-ecd6-7f61-93e6-5d428fef64f5/ig_00c0a8afbafc1ecf016a3b0a6c51b081919c42cc9c4cfd9d3e.png`

## 5. Notes for implementation
- Manter o shell dark como padrão.
- Evitar cardosidade excessiva e texto competindo no mesmo viewport.
- Preservar a estrutura existente de Apoema, mas com aparência de app desktop nativo.
