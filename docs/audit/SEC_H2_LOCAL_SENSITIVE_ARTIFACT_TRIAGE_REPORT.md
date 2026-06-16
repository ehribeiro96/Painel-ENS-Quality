# SEC-H2 — Local Sensitive Artifact Triage

Boundary: `SEC-H2 — local sensitive artifact triage`
Modo: auditoria conservadora por metadados, sem correção.

## Resumo executivo

Status: `GO COM RESSALVAS`.
Motivo: os itens sensíveis locais foram triados por metadados, tracking/stage/history foram verificados, a proteção por ignore foi verificada e a proposta de ignore/plano manual foram criados. A ressalva é que a revisão humana continua obrigatória para `123`, `123.pub`, `imports/` e grupos com nomes sensíveis; nenhum conteúdo sensível foi aberto.
Stage inicial/final: inicial vazio; final deve permanecer vazio conforme FASE 11.
Nenhum conteúdo sensível aberto: confirmado para `123`, `123.pub`, `imports/`, DOCX grande, planilhas, binários grandes, screenshots operacionais, dumps, bancos, tokens e credenciais.

## Escopo

Itens/grupos analisados:

- `123`
- `123.pub`
- `imports/`
- nomes sensíveis em untracked por path
- referências em arquivos tracked seguros, resumidas por arquivo, sem imprimir valores
- proteção atual por `.gitignore` via `git check-ignore`, sem alterar ignore

Fora de escopo: abrir conteúdo, apagar, mover, renomear, stagear, commitar, push, editar `.gitignore`, limpar histórico ou corrigir código.

## Itens analisados por metadados

### `123`

- Existe: sim.
- Tipo: arquivo regular.
- Permissão: `-rw-------`.
- Tamanho: 464 bytes.
- Classificação: `S0_NEVER_OPEN_NEVER_COMMIT`.
- Interpretação: tamanho/modo são compatíveis com artefato local sensível; não houve leitura de conteúdo.

### `123.pub`

- Existe: sim.
- Tipo: arquivo regular.
- Permissão: `-rw-r--r--`.
- Tamanho: 108 bytes.
- Classificação: `S1_LOCAL_SECRET_CANDIDATE`.
- Interpretação: mesmo se for chave pública, não deve ser impresso nem commitado sem decisão humana.

### `imports/`

- Existe: sim.
- Tipo: diretório.
- Permissão: `drwxr-xr-x`.
- Itens listados por metadados/path, sem conteúdo:
  - `imports/HermesOps-Final-Transfer/IMPORT_MANIFEST.txt`
  - `imports/HermesOps-Final-Transfer/ROLLBACK_INSTRUCTIONS.md`
  - `imports/HermesOps-Final-Transfer/IMPORT_REPORT.md`
  - `imports/HermesOps-Final-Transfer/current` symlink
  - subdiretórios `releases/...`
- Classificação: `S2_LOCAL_DATA_DO_NOT_COMMIT`.
- Interpretação: deve ficar fora do Git até revisão humana; se algo virar fixture, recriar anonimizadamente em boundary própria.

## Git tracking/history check

Resultado para `123`, `123.pub` e `imports/`:

| Checagem | Resultado | Interpretação |
|---|---|---|
| `git ls-files -- 123 123.pub imports` | sem saída | não estão tracked atualmente |
| `git diff --cached --name-status -- 123 123.pub imports` | sem saída | não estão staged |
| `git status --short -- 123 123.pub imports` | `?? 123`, `?? 123.pub`, `?? imports/` | continuam untracked |
| `git log --all --oneline -- 123 123.pub imports` | sem saída | não foi detectado histórico Git para esses paths |

Decisão: não há evidência local de tracking/stage/history para esses três paths. Não há `S4_HISTORY_RISK` confirmado nesta boundary.

## Ignore atual

`git check-ignore -v` para `123`, `123.pub` e amostra de arquivos em `imports/` não retornou regra aplicável.

Interpretação: os itens permanecem desprotegidos por ignore atual. Classificação adicional: `S5_IGNORE_PATTERN_NEEDED`.

Não foi feita alteração em `.gitignore`.

## Nomes sensíveis em untracked por path

Total de hits por path: 24.

| Path | Motivo | Ação |
|---|---|---|
| `123` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `123.pub` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `_cleanup_backup_manifest.md` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `_migration_proposals/hermesops_selective_migration/docs/hermesops/knowledge/service-desk/_seed/certificates/certificado-a3-token-smartcard.md` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/config/database.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/database/.gitignore` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/database/factories/UserFactory.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/database/migrations/2014_10_12_000000_create_users_table.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/database/migrations/2014_10_12_200000_add_two_factor_columns_to_users_table.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/database/migrations/2019_08_19_000000_create_failed_jobs_table.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/database/migrations/2022_03_23_163443_create_sessions_table.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/database/migrations/2022_05_11_154250_create_datafeeds_table.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/database/seeders/DashboardTableSeeder.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/database/seeders/DatabaseSeeder.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/lang/en/passwords.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/resources/views/api/api-token-manager.blade.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/resources/views/auth/confirm-password.blade.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/resources/views/auth/forgot-password.blade.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/resources/views/auth/reset-password.blade.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/resources/views/components/confirms-password.blade.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `assets/legacy/Laravel/resources/views/profile/update-password-form.blade.php` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `imports/HermesOps-Final-Transfer/IMPORT_MANIFEST.txt` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `imports/HermesOps-Final-Transfer/IMPORT_REPORT.md` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |
| `imports/HermesOps-Final-Transfer/ROLLBACK_INSTRUCTIONS.md` | path contém nome/padrão sensível ou pertence a imports | revisão por metadados somente |

Observação: a classificação acima usa somente nomes de paths. Não houve leitura do conteúdo desses arquivos.

## Referências em tracked files seguros

A busca por nomes/padrões sensíveis em arquivos tracked foi resumida por arquivo para evitar impressão de valores. Total de hits: 12425.

| Arquivo tracked | Hits |
|---|---:|
| `docs/audit/FILE_CLASSIFICATION.csv` | 5698 |
| `docs/audit/PROJECT_TREE.txt` | 5676 |
| `frontend/itam-platform/src/lib/api.ts` | 71 |
| `docs/WORKTREE_TRIAGE_REPORT.md` | 52 |
| `backend/app/api/v1/routes/auth.py` | 25 |
| `docs/audit/WORKTREE_BOUNDARY_COMMIT_PLAN_GIT_C1.md` | 22 |
| `docs/IMPORT_PIPELINE_STAGING_B3_REPORT.md` | 21 |
| `tests/test_ai_chat_mvp.py` | 21 |
| `docs/IMPORT_SERVICE_REFACTOR_PLAN.md` | 20 |
| `docs/IMPORT_SERVICE_REFACTOR_MANIFEST.md` | 20 |
| `backend/app/domains/ai_chat/providers.py` | 19 |
| `tests/test_imports_regression.py` | 19 |
| `frontend/itam-platform/src/pages/ImportsPage.tsx` | 18 |
| `docs/audit/GIT_H2_UNTRACKED_SAFETY_TRIAGE_REPORT.md` | 17 |
| `docs/IMPORT_SERVICE_REFACTOR_REPORT.md` | 17 |
| `backend/app/domains/auth/service.py` | 16 |
| `frontend/itam-platform/src/pages/AiChatPage.tsx` | 16 |
| `docs/TRACKED_HYGIENE_CANDIDATES_S1C.txt` | 15 |
| `tests/operational_http.py` | 14 |
| `docs/hermesops/service-desk/_seed/certificates/certificado-a3-token-smartcard.md` | 14 |
| `frontend/itam-platform/src/lib/auth.tsx` | 13 |
| `docs/HERMES_SELF_CONFIG_HARDENING_PLAN.md` | 13 |
| `docs/audit/HERMES_FULL_PROJECT_AUDIT_H1_REPORT.md` | 13 |
| `docs/audit/GIT_H2_UNTRACKED_INVENTORY.csv` | 13 |
| `docs/RUFF_BASELINE.txt` | 12 |

Interpretação: a maior parte dos hits está em inventários/relatórios históricos (`FILE_CLASSIFICATION.csv`, `PROJECT_TREE.txt`, relatórios de auditoria), documentação, testes e código que naturalmente contém termos como token/password/imports. Não foi confirmado segredo real nesta boundary porque a busca não foi usada para imprimir valores, apenas para mapear presença de referências.

## Classificação de risco

| Path/grupo | Categoria | Motivo | Pode abrir? | Pode commitar? | Ação recomendada |
|---|---|---|---|---|---|
| `123` | `S0_NEVER_OPEN_NEVER_COMMIT` | arquivo local com nome opaco, permissão restritiva e tamanho compatível com artefato sensível | não no Hermes | não | revisão manual fora do Hermes; mover/remover só por humano |
| `123.pub` | `S1_LOCAL_SECRET_CANDIDATE` | possível chave pública/artefato associado | não imprimir | não sem decisão | revisão manual; se chave SSH, armazenar corretamente fora do repo |
| `imports/` | `S2_LOCAL_DATA_DO_NOT_COMMIT` | dados/artefatos locais de importação | não nesta boundary | não | manter fora do Git; criar fixtures anonimizadas se necessário |
| screenshots com imports | `S3_BINARY_OR_DOC_REVIEW` | podem conter dados operacionais de UI | não/OCR proibido | não agora | revisar em DOCS-H2/SEC-H2 visual separado |
| `_migration_proposals/` com nomes sensíveis | `S7_HUMAN_REVIEW_REQUIRED` | propostas contêm paths de segurança/token/certificado/password | somente filtros por metadata/path | não agora | revisar por docs/security boundary |
| `assets/legacy/Laravel/database*` e `password*` | `S7_HUMAN_REVIEW_REQUIRED` | path legacy com nomes de banco/senha; pode ser código template | somente boundary legacy | não agora | LEGACY-H2 |
| `assets/static/Guia_Assinatura_ENS_Ilustrado_v1.docx` | `S3_BINARY_OR_DOC_REVIEW` | DOCX grande/binário | não | não agora | decisão manual: LFS/artifact/storage/ignore |

## Itens que nunca devem ser commitados

- `123`
- `123.pub`, salvo decisão humana explícita e justificativa forte; recomendação padrão é não commitar
- `imports/`
- `*.pem`, `*.key`, `*.pfx`, `*.p12`, `*.crt`, `*.cer`, `*.der`, `*.kdbx`
- bancos/dumps/backups locais: `*.sqlite`, `*.sqlite3`, `*.db`, `*.dump`, `*.bak`, `*.sql`
- screenshots ou documentos com dados operacionais reais
- qualquer arquivo com segredo, token, credencial, certificado ou chave

## Itens que exigem revisão humana

- `123`
- `123.pub`
- `imports/`
- `_migration_proposals/` com paths sensíveis
- `assets/legacy/` e paths de Laravel relacionados a database/password/token
- DOCX grande do guia ilustrado
- screenshots antigas, principalmente com `imports` no path
- `_audit_findings/`
- `ai-lab/` se contiver resultados/benchmarks locais

## Proposta de .gitignore

Ver `docs/audit/SEC_H2_GITIGNORE_PROPOSAL.md`.

A proposta é documental e não foi aplicada.

## Plano manual

Ver `docs/audit/SEC_H2_MANUAL_ACTIONS.md`.

O plano é documental e não foi executado.

## Riscos restantes

1. `123`/`123.pub` ainda existem no root do repo e não estão ignorados.
2. `imports/` ainda existe no root do repo e não está ignorado.
3. Há 723 untracked no início da boundary SEC-H2, incluindo relatórios e grupos antigos.
4. `docs/audit/FILE_CLASSIFICATION.csv` e `PROJECT_TREE.txt` referenciam muitos paths; consolidar documentação antes de commit amplo.
5. `assets/legacy/` tem paths sensíveis por nome e precisa de boundary própria.
6. `.gitignore` não protege os padrões propostos, mas não deve ser alterado sem `IGNORE-H2`.

## Próximas boundaries recomendadas

1. `DOCS-H2 — audit docs consolidation`.
2. `IGNORE-H2 — gitignore hygiene for local artifacts`.
3. `CI-H2 — GitHub Actions docker build/push review`.
4. `LEGACY-H2 — legacy assets and DOCX large artifact decision`.
5. `TEST-H2 — pytest markers and validation standardization`.
6. `SEC-H3 — sensitive artifact manual remediation`, somente se revisão humana indicar segredo real ou histórico/tracked em algum item futuro.

## Decisão final

`GO COM RESSALVAS`: a triagem por metadados foi concluída sem abrir conteúdo sensível e sem detectar que `123`, `123.pub` ou `imports/` estejam tracked/staged/no histórico local. A ação recomendada é proteger esses padrões em `IGNORE-H2` e fazer revisão manual fora do Hermes antes de qualquer remoção/movimentação.
