# LEGACY-H2 — Asset Reference Matrix

Boundary: `LEGACY-H2 — legacy assets and DOCX large artifact decision`

Esta matriz foi produzida por inventário de metadados e busca textual segura. DOCX e imagens não foram abertos. Nenhum asset foi stageado ou commitado nesta boundary.

## Resumo de inventário

| Grupo | Quantidade | Tamanho observado | Observação |
|---|---:|---:|---|
| `assets/legacy/` diretórios | 58 | n/a | Tree legado Laravel/hero preservado fora de stage |
| `assets/legacy/` arquivos | 218 | 4.382.052 bytes | Inclui Laravel antigo, `hero.js`, sourcemap e imagens legadas |
| `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx` | 1 | 11.700.117 bytes | DOCX grande; não aberto |
| `assets/static/icons/Logo.png` | 1 | 14.243 bytes | Imagem untracked; não aberta |
| Ícones sociais untracked | 5 | 3.365 bytes | `facebook`, `instagram`, `linkedin`, `tiktok`, `youtube`; não abertos |
| `assets/static/icons/.gitkeep` | 1 | 1 byte | Arquivo marcador untracked |

## Matrix

| Path/Grupo | Referenciado? | Onde | Tipo | Tamanho | Decisão | Motivo | Boundary futura |
|---|---|---|---|---:|---|---|---|
| `assets/legacy/` | Apenas docs/relatórios; não comprovado em runtime atual | `docs/PROJECT_CLEANUP_AUDIT.md`, `docs/WORKTREE_TRIAGE_REPORT.md`, docs históricos | Diretório legado | 218 arquivos / 4.382.052 bytes | `LEGACY_ARCHIVE_DEFER` | Tree legado amplo; não deve entrar em commit misturado; sem referência runtime atual comprovada | `LEGACY-H3` se houver decisão humana |
| `assets/legacy/hero.js` | Não comprovado em runtime atual; mencionado por inventário/docs | Bundle legado e minificado | JS minificado | 600.107 bytes | `EXTERNAL_REFERENCE_RISK;LEGACY_ARCHIVE_DEFER` | Scan encontrou saída minificada grande; requer revisão manual se for preservar como histórico | `LEGACY-H3` |
| `assets/legacy/hero.js.map` | Não comprovado em runtime atual | Inventário apenas | sourcemap | 2.675.163 bytes | `LEGACY_ARCHIVE_DEFER;IGNORE_CANDIDATE_FUTURE` | Sourcemap grande de bundle legado; candidato a tratamento/ignore futuro se não houver valor histórico | `LEGACY-H3` |
| `assets/legacy/Laravel/` | Apenas docs/relatórios; não comprovado em runtime atual | `docs/WORKTREE_TRIAGE_REPORT.md` e docs antigos | App Laravel legado | parte dos 4.382.052 bytes | `LEGACY_ARCHIVE_DEFER` | Arquivo histórico/protótipo legado, não runtime canônico FastAPI/React atual | `LEGACY-H3` |
| `assets/legacy/Laravel/README.md` | Não runtime | Scan externo encontrou links documentais | Markdown legado | 4.631 bytes | `EXTERNAL_REFERENCE_RISK;LEGACY_ARCHIVE_DEFER` | Contém links externos documentais/social do template antigo | `LEGACY-H3` |
| `assets/legacy/Laravel/resources/js/components/dashboard-card-*.js` | Não runtime atual comprovado | Scan externo encontrou comentários para Chart.js | JS legado | múltiplos arquivos | `EXTERNAL_REFERENCE_RISK;LEGACY_ARCHIVE_DEFER` | Referências externas documentais em comentários; não corrigir nesta boundary | `LEGACY-H3` |
| `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx` | Sim, em legado Flask; não comprovado no runtime FastAPI atual | `src/legacy/flask_app.py`, docs históricos | DOCX grande | 11.700.117 bytes | `BINARY_LARGE_HUMAN_REVIEW` | Arquivo binário grande; não aberto; decisão humana obrigatória para download público/histórico/ignore | `LEGACY-H3` |
| `assets/static/icons/Logo.png` | Sim | `backend/app/domains/signatures/service.py:79`; também `src/legacy/flask_app.py` e docs | Imagem | 14.243 bytes | `REQUIRED_RUNTIME_ASSET;IMAGE_HUMAN_REVIEW;COMMIT_CANDIDATE_FUTURE` | Backend atual tenta carregar `icons/Logo.png`; imagem não aberta e não commitada nesta boundary | Boundary futura de assets runtime aprovada |
| `assets/static/icons/facebook.png` | Referência local não comprovada em runtime atual | URL externa homônima em `src/legacy/flask_app.py`; docs antigos | Imagem social | 467 bytes | `IMAGE_HUMAN_REVIEW;COMMIT_CANDIDATE_FUTURE` | Pode substituir referência externa legada, mas requer decisão humana; não abrir imagem nesta boundary | `LEGACY-H3` ou assets runtime futura |
| `assets/static/icons/instagram.png` | Referência local não comprovada em runtime atual | URL externa homônima em `src/legacy/flask_app.py`; docs antigos | Imagem social | 992 bytes | `IMAGE_HUMAN_REVIEW;COMMIT_CANDIDATE_FUTURE` | Pode substituir referência externa legada, mas requer decisão humana | `LEGACY-H3` ou assets runtime futura |
| `assets/static/icons/linkedin.png` | Referência local não comprovada em runtime atual | URL externa homônima em `src/legacy/flask_app.py`; docs antigos | Imagem social | 553 bytes | `IMAGE_HUMAN_REVIEW;COMMIT_CANDIDATE_FUTURE` | Pode substituir referência externa legada, mas requer decisão humana | `LEGACY-H3` ou assets runtime futura |
| `assets/static/icons/tiktok.png` | Referência local não comprovada em runtime atual | URL externa homônima em `src/legacy/flask_app.py` | Imagem social | 664 bytes | `IMAGE_HUMAN_REVIEW;COMMIT_CANDIDATE_FUTURE` | Pode substituir referência externa legada, mas requer decisão humana | `LEGACY-H3` ou assets runtime futura |
| `assets/static/icons/youtube.png` | Referência local não comprovada em runtime atual | URL externa homônima em `src/legacy/flask_app.py`; docs antigos | Imagem social | 689 bytes | `IMAGE_HUMAN_REVIEW;COMMIT_CANDIDATE_FUTURE` | Pode substituir referência externa legada, mas requer decisão humana | `LEGACY-H3` ou assets runtime futura |
| `assets/static/icons/.gitkeep` | Não | Status untracked apenas | marcador | 1 byte | `UNREFERENCED_LOCAL_ARTIFACT` | Marcador de diretório; só versionar se boundary futura decidir versionar diretório/ícones | Boundary futura de assets |

## Decisão consolidada

- `assets/legacy/`: preservar como `LEGACY_ARCHIVE_DEFER`; não commitar agora.
- DOCX grande: `BINARY_LARGE_HUMAN_REVIEW`; não abrir, extrair, converter ou commitar agora.
- `Logo.png`: tem sinal de necessidade runtime pelo backend atual, mas é imagem untracked e exige aprovação humana antes de commit.
- Ícones sociais: sem referência local comprovada no runtime atual; candidatos a revisão humana/commit futuro se a estratégia for remover URLs externas do legado.
- Nenhum asset foi stageado nesta boundary.
