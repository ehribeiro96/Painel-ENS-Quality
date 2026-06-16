# LEGACY-H2 — Remaining Legacy Assets and DOCX Decision

Boundary: `LEGACY-H2 — legacy assets and DOCX large artifact decision`

## Resumo executivo

Status: `GO` documental para inventário e decisão conservadora.
Stage inicial/final: inicial vazio; final deve ser confirmado após commit documental.
Assets commitados nesta boundary: não.
DOCX aberto: não.
OCR usado: não.

Decisão curta:

- Não commitar `assets/legacy/` agora.
- Não commitar `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx` agora.
- Não commitar imagens agora.
- `Logo.png` tem evidência de uso pelo backend atual e deve ser tratado em boundary futura específica de assets runtime, com aprovação humana.
- Ícones sociais têm indícios de relação com URLs externas do legado, mas não tiveram uso local runtime comprovado nesta boundary.
- `assets/legacy/hero.js` é minificado/volumoso e exige revisão futura se alguém decidir preservar esse archive.

## Escopo

Escopo permitido nesta boundary:

- Inventário por metadados de `assets/legacy/`.
- Inventário por metadados do DOCX grande.
- Inventário por metadados de `Logo.png` e ícones sociais.
- Busca textual por referências seguras, sem abrir binários.
- Criação de documentação e matriz de decisão.
- Commit documental apenas dos relatórios LEGACY-H2 e índices permitidos.

Fora de escopo executado como não feito:

- Nenhum asset foi alterado.
- Nenhum asset foi stageado.
- Nenhum DOCX foi aberto, extraído, convertido ou analisado por conteúdo.
- Nenhuma imagem foi aberta ou analisada visualmente.
- Nenhum OCR foi usado.
- Nenhum template, CSS, JS funcional, Docker/Compose, migration, package-lock ou código de aplicação foi alterado.

## Itens analisados por metadados

### `assets/legacy/`

- Diretórios: 58.
- Arquivos: 218.
- Tamanho total de arquivos: 4.382.052 bytes.
- Sufixos principais:
  - `.php`: 159 arquivos.
  - sem extensão: 16 arquivos.
  - `.js`: 15 arquivos.
  - `.jpg`: 6 arquivos.
  - `.svg`: 5 arquivos.
  - `.css`: 4 arquivos.
  - `.md`: 3 arquivos.
  - `.json`: 2 arquivos.
  - `.map`: 1 arquivo.
  - `.xml`, `.example`, `.lock`, `.yaml`, `.ico`, `.txt`: 1 arquivo cada.

Maiores arquivos observados:

| Arquivo | Tamanho |
|---|---:|
| `assets/legacy/hero.js.map` | 2.675.163 bytes |
| `assets/legacy/hero.js` | 600.107 bytes |
| `assets/legacy/Laravel/composer.lock` | 328.205 bytes |
| `assets/legacy/Laravel/public/images/auth-image.jpg` | 232.046 bytes |
| `assets/legacy/Laravel/resources/views/components/app/sidebar.blade.php` | 72.604 bytes |

### DOCX

- Path: `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`.
- Tamanho: 11.700.117 bytes.
- Tipo: regular file.
- Status Git: untracked.
- Conteúdo: não aberto.

### Logo e ícones

- `assets/static/icons/Logo.png`: 14.243 bytes; untracked; não aberto.
- `assets/static/icons/facebook.png`: 467 bytes; untracked; não aberto.
- `assets/static/icons/instagram.png`: 992 bytes; untracked; não aberto.
- `assets/static/icons/linkedin.png`: 553 bytes; untracked; não aberto.
- `assets/static/icons/tiktok.png`: 664 bytes; untracked; não aberto.
- `assets/static/icons/youtube.png`: 689 bytes; untracked; não aberto.
- `assets/static/icons/.gitkeep`: 1 byte; untracked.

## Referências encontradas

### Referências relevantes por busca textual

- `backend/app/domains/signatures/service.py:79` chama `_image_data_uri("icons/Logo.png", "icons/logo.png")`.
- `src/legacy/flask_app.py` referencia `Guia_Assinatura_ENS_Ilustrado_v1.docx` como arquivo estático de guia.
- `src/legacy/flask_app.py` contém URLs externas para logo e ícones sociais hospedados fora do repositório.
- Docs históricos mencionam `assets/legacy/`, `Logo.png`, ícones sociais e o DOCX.

### Classificação de referência

- `assets/legacy/`: não teve uso runtime atual comprovado; aparece em docs/inventários antigos.
- DOCX grande: referenciado pelo legado Flask; não comprovado como necessário ao runtime FastAPI atual; decisão humana obrigatória.
- `Logo.png`: referenciado por backend atual; provável asset runtime necessário, mas imagem não foi aberta nem commitada nesta boundary.
- Ícones sociais: referências locais não comprovadas no runtime atual; o legado usa URLs externas homônimas.

## assets/legacy/

Classificação: `LEGACY_ARCHIVE_DEFER`.

Motivos:

- Tree amplo, misturando app Laravel antigo, bundle minificado, sourcemap, imagens e templates.
- Não há evidência de que `assets/legacy/` seja carregado pelo runtime FastAPI/React atual.
- Já havia decisão anterior de preservar sem commit misturado.
- Pode ter valor histórico, mas precisa decisão humana para arquivamento, ignore ou descarte manual.

Decisão: não commitar nesta boundary.

## Guia_Assinatura_ENS_Ilustrado_v1.docx

Classificação: `BINARY_LARGE_HUMAN_REVIEW`.

Motivos:

- DOCX grande: 11.700.117 bytes.
- Arquivo binário; não foi aberto, extraído ou convertido.
- Referenciado por `src/legacy/flask_app.py`, mas a necessidade no runtime atual não foi decidida.
- Pode ser material de download público, histórico ou artefato local.

Decisão: não commitar nesta boundary; exigir decisão humana antes de qualquer versionamento.

## Logo.png e ícones

### `Logo.png`

Classificação: `REQUIRED_RUNTIME_ASSET;IMAGE_HUMAN_REVIEW;COMMIT_CANDIDATE_FUTURE`.

Motivos:

- Há referência direta em backend atual: `backend/app/domains/signatures/service.py:79`.
- O arquivo está untracked.
- A imagem não foi aberta nem validada visualmente.
- Como é asset potencialmente runtime, não deve ser tratado junto com archive legado amplo.

Decisão: não commitar nesta boundary; abrir boundary futura específica para assets runtime se aprovado.

### Ícones sociais

Classificação: `IMAGE_HUMAN_REVIEW;COMMIT_CANDIDATE_FUTURE`.

Motivos:

- Arquivos existem localmente e estão untracked.
- Referências locais diretas no runtime atual não foram comprovadas.
- `src/legacy/flask_app.py` ainda usa URLs externas homônimas para esses ícones.
- Podem ser úteis para substituir dependência externa, mas isso é alteração funcional/visual de legado e exige boundary própria.

Decisão: não commitar nesta boundary.

## Referências externas

Classificação: `EXTERNAL_REFERENCE_RISK`.

Achados:

- `assets/legacy/Laravel/README.md` contém links externos documentais do template antigo.
- Componentes dashboard legados contêm comentários com URL de Chart.js.
- `assets/legacy/hero.js` gerou saída minificada grande; análise detalhada interrompida e classificada como `LEGACY_MINIFIED_REVIEW_REQUIRED`.
- `src/legacy/flask_app.py` contém URLs externas para logo e ícones sociais em hospedagem SharePoint/OneDrive corporativa.

Decisão: registrar risco; não corrigir nesta boundary.

## Classificação de decisão

| Categoria | Aplicação nesta boundary |
|---|---|
| `REQUIRED_RUNTIME_ASSET` | `assets/static/icons/Logo.png` por referência no backend atual |
| `PUBLIC_DOWNLOAD_CANDIDATE` | DOCX grande, se humano confirmar que deve ser download público |
| `LEGACY_ARCHIVE_DEFER` | `assets/legacy/` e Laravel/bundle legado |
| `EXTERNAL_REFERENCE_RISK` | URLs/comments externos em legado e URLs externas em `src/legacy/flask_app.py` |
| `BINARY_LARGE_HUMAN_REVIEW` | DOCX grande |
| `IMAGE_HUMAN_REVIEW` | `Logo.png` e ícones sociais |
| `UNREFERENCED_LOCAL_ARTIFACT` | `.gitkeep` e possivelmente ícones sociais se decisão humana rejeitar uso |
| `IGNORE_CANDIDATE_FUTURE` | `hero.js.map` e/ou DOCX se confirmado como local/não versionável |
| `COMMIT_CANDIDATE_FUTURE` | `Logo.png`; possivelmente ícones sociais e DOCX se aprovado |
| `DO_NOT_TOUCH` | Todo asset nesta boundary |

## Itens que NÃO devem ser commitados agora

- `assets/legacy/`
- `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx`
- `assets/static/icons/Logo.png`
- `assets/static/icons/facebook.png`
- `assets/static/icons/instagram.png`
- `assets/static/icons/linkedin.png`
- `assets/static/icons/tiktok.png`
- `assets/static/icons/youtube.png`
- `assets/static/icons/.gitkeep`

## Itens que exigem aprovação humana

1. `Logo.png`: decidir se deve ser versionado como asset runtime mínimo.
2. Ícones sociais: decidir se substituirão URLs externas do legado ou se são artefatos locais.
3. DOCX grande: decidir se é material público de download, histórico, artefato local ou candidato a ignore.
4. `assets/legacy/`: decidir entre archive versionado, pacote externo, ignore, descarte manual ou documentação histórica.
5. `hero.js`/`hero.js.map`: decidir se há valor histórico suficiente para preservar.

## Próximas boundaries recomendadas

1. `TEST-H2 — pytest markers and validation standardization`.
2. `LEGACY-H3 — legacy archive/manual artifact handling`, se decisão humana aprovar.
3. `CI-H4 — publish workflow design`, somente com decisão humana.
4. `SEC-H3`, somente se revisão humana confirmar necessidade.

## Decisão final

`LEGACY-H2` conclui com decisão conservadora:

- `assets/legacy/`: `LEGACY_ARCHIVE_DEFER`, sem commit.
- DOCX grande: `BINARY_LARGE_HUMAN_REVIEW`, sem abertura e sem commit.
- `Logo.png`: `REQUIRED_RUNTIME_ASSET` provável, mas `IMAGE_HUMAN_REVIEW` e sem commit nesta boundary.
- Ícones sociais: `IMAGE_HUMAN_REVIEW`, sem commit.
- Referências externas: documentadas como `EXTERNAL_REFERENCE_RISK`, sem correção nesta boundary.

Somente documentos LEGACY-H2 devem ser stageados/commitados.
