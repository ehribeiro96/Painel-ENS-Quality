# LEGACY-H2 — External Reference Scan

Boundary: `LEGACY-H2 — legacy assets and DOCX large artifact decision`

Este scan foi restrito a arquivos texto em `assets/legacy/` e a buscas textuais seguras. DOCX e imagens não foram abertos. Blocos minificados não foram colados integralmente.

## Arquivos texto legados verificados

Arquivos texto listados por extensão segura (`.html`, `.css`, `.js`, `.txt`, `.md`) dentro de `assets/legacy/`:

- `assets/legacy/Laravel/README.md`
- `assets/legacy/Laravel/postcss.config.js`
- `assets/legacy/Laravel/public/robots.txt`
- `assets/legacy/Laravel/resources/css/additional-styles/flatpickr.css`
- `assets/legacy/Laravel/resources/css/additional-styles/utility-patterns.css`
- `assets/legacy/Laravel/resources/css/app.css`
- `assets/legacy/Laravel/resources/js/app.js`
- `assets/legacy/Laravel/resources/js/bootstrap.js`
- `assets/legacy/Laravel/resources/js/components/dashboard-card-01.js`
- `assets/legacy/Laravel/resources/js/components/dashboard-card-02.js`
- `assets/legacy/Laravel/resources/js/components/dashboard-card-03.js`
- `assets/legacy/Laravel/resources/js/components/dashboard-card-04.js`
- `assets/legacy/Laravel/resources/js/components/dashboard-card-05.js`
- `assets/legacy/Laravel/resources/js/components/dashboard-card-06.js`
- `assets/legacy/Laravel/resources/js/components/dashboard-card-08.js`
- `assets/legacy/Laravel/resources/js/components/dashboard-card-09.js`
- `assets/legacy/Laravel/resources/js/components/dashboard-card-11.js`
- `assets/legacy/Laravel/resources/js/utils.js`
- `assets/legacy/Laravel/resources/markdown/policy.md`
- `assets/legacy/Laravel/resources/markdown/terms.md`
- `assets/legacy/Laravel/vite.config.js`
- `assets/legacy/ens-hero-client.css`
- `assets/legacy/hero.js`

## Arquivos com referências externas ou termos sensíveis por nome

A busca por URLs externas e termos de risco retornou estes arquivos:

| Arquivo | Tipo de referência | Risco | Ação recomendada | Correção futura? | Runtime atual? |
|---|---|---|---|---|---|
| `assets/legacy/Laravel/README.md` | Links externos para GitHub/Twitter/Cruip do template antigo | Baixo, documental/histórico | Preservar apenas se o archive legado for aprovado; não misturar com runtime | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/Laravel/resources/js/bootstrap.js` | Match por termo de scan em JS legado | Baixo/inconclusivo | Revisar somente se Laravel legado for preservado | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/Laravel/resources/js/components/dashboard-card-01.js` | Comentário externo para Chart.js | Baixo, referência documental | Sem correção nesta boundary | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/Laravel/resources/js/components/dashboard-card-02.js` | Comentário externo para Chart.js | Baixo, referência documental | Sem correção nesta boundary | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/Laravel/resources/js/components/dashboard-card-03.js` | Comentário externo para Chart.js | Baixo, referência documental | Sem correção nesta boundary | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/Laravel/resources/js/components/dashboard-card-04.js` | Comentário externo para Chart.js | Baixo, referência documental | Sem correção nesta boundary | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/Laravel/resources/js/components/dashboard-card-05.js` | Comentário externo para Chart.js | Baixo, referência documental | Sem correção nesta boundary | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/Laravel/resources/js/components/dashboard-card-06.js` | Comentário externo para Chart.js | Baixo, referência documental | Sem correção nesta boundary | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/Laravel/resources/js/components/dashboard-card-08.js` | Comentário externo para Chart.js | Baixo, referência documental | Sem correção nesta boundary | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/Laravel/resources/js/components/dashboard-card-09.js` | Comentário externo para Chart.js | Baixo, referência documental | Sem correção nesta boundary | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/Laravel/resources/js/components/dashboard-card-11.js` | Comentário externo para Chart.js | Baixo, referência documental | Sem correção nesta boundary | Opcional em `LEGACY-H3` | Não comprovado |
| `assets/legacy/hero.js` | Bundle minificado com muitas strings externas/dependências | Médio/inconclusivo | Não colar minificado; classificar como `LEGACY_MINIFIED_REVIEW_REQUIRED` | Sim, se archive for aprovado | Não comprovado |

## Amostras seguras observadas

- `assets/legacy/Laravel/resources/js/components/dashboard-card-*.js`: comentários `https://www.chartjs.org/`.
- `assets/legacy/Laravel/README.md`: links documentais para GitHub, Twitter e Cruip do template antigo.
- `assets/legacy/hero.js`: saída minificada gigante; análise detalhada interrompida para evitar ruído e exposição desnecessária.

## Referências externas fora de `assets/legacy/`

Busca focada também mostrou que `src/legacy/flask_app.py` ainda contém URLs externas para imagens sociais e logo em endpoint SharePoint/OneDrive corporativo. Isto não foi alterado nesta boundary.

Classificação:

- Tipo: `EXTERNAL_REFERENCE_RISK` em runtime legado.
- Risco: dependência externa/frágil para assets que parecem ter equivalentes locais untracked em `assets/static/icons/`.
- Ação recomendada: boundary futura para decidir se os ícones locais devem substituir URLs externas, com aprovação humana e validação do legado `/admin` e `/assinaturas`.

## Segredos

A busca por termos como `token`, `secret`, `password` em `assets/legacy/` foi usada apenas como triagem textual. Nesta boundary não foi identificado valor real de segredo nos outputs preservados. Termos sensíveis aparecem como palavras de código/teste/config legado ou em documentação redigida antiga.

## Decisão

- Não corrigir referências externas nesta boundary.
- Não commitar `assets/legacy/` nesta boundary.
- Não abrir imagens ou DOCX.
- Abrir `LEGACY-H3` somente se houver decisão humana para arquivar, ignorar ou portar material legado.
