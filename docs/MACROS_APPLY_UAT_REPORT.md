# Macros Apply UAT Report

## Resumo executivo

O Apply controlado das macros oficiais foi executado no PostgreSQL UAT usando exclusivamente a fonte atual do projeto `quality_macros_project`.

O Apply do `ens.db` nao foi executado. A confirmacao `APPLY_LEGACY_ENS_DB` nao foi usada. O arquivo antigo de macros em `[PROJETO]\MACRO` nao foi usado.

## Ambiente

- Projeto Docker Compose: `itam_uat`
- Fonte oficial de macros: `C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json`
- Fonte oficial de hints: `C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\colaboradores.json`
- Alembic: `0005_macros_module (head)`
- Tabelas confirmadas:
  - `macro_templates`
  - `macro_generations`
  - `macro_autocomplete_hints`

## Backup

Backups UAT criados antes dos Applies:

- `backups\itam_backup_20260603_000018.dump`
- `backups\itam_backup_20260603_000018.manifest.json`
- `backups\itam_backup_20260603_000532.dump`
- `backups\itam_backup_20260603_000532.manifest.json`

## Apply das macros oficiais

Comando executado:

```powershell
python scripts/import_quality_macros_to_postgres.py --json-path "C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json" --mode Apply --confirm-apply APPLY_MACROS_JSON
```

Relatorio gerado:

```text
uat_evidence\macros_import\macros_json_apply_20260603_030052.json
```

Resultado:

- total lido: `7`
- validos: `7`
- criados: `7`
- atualizados: `0`
- ignorados: `0`
- invalidos: `0`
- falhas: `0`

Templates criados:

- `[Suporte] Contato inicial`
- `[Suporte] Resolvido`
- `[Suporte] Continuar atendimento`
- `[Suporte] Agendamento de Prova 0800`
- `[Suporte] Tentativa de contato`
- `[Ativos] Atualizar inventário`
- `[Infraestrutura] Encaminhamento`

Validacoes no banco:

- `macro_templates = 7`
- slug `ativos-atualizar-inventario` criado
- nenhum slug duplicado identificado
- `source = macros_json`

## Validacao da API e frontend

Validacoes executadas:

- `GET /api/v1/macros/templates` com token retornou `7` templates.
- `GET /api/v1/macros/templates` sem token retornou `401`.
- `POST /api/v1/macros/render` renderizou macro com campos completos.
- `POST /api/v1/macros/render` retornou erro funcional para campos obrigatorios ausentes.
- `GET /macros` retornou `200`.

Rotas criticas preservadas:

- `GET /health` retornou `200`.
- `GET /` retornou `200`.
- `GET /assinaturas/` retornou `200`.
- `GET /admin/` retornou `302`.
- `GET /api/v1/assets` sem token retornou `401`.

## Macro de movimentacao

Foi validado movimento existente:

```text
312dca3b-ce95-4194-b14c-0baf20344ff4
```

Endpoint validado:

```text
GET /api/v1/movements/{movement_id}/suggested-macro
```

Resultado:

- status: sucesso
- template usado: `ativos-atualizar-inventario`
- texto renderizado contem `Atualizar Inventário`
- campos pendentes identificados: `Usuário Anterior`, `Usuário Atual`

Ajuste aplicado:

- O renderer agora diferencia lista de campos obrigatorios ausente de lista vazia intencional.
- A macro sugerida preserva placeholders pendentes em vez de retornar erro 500.

## Apply dos hints

Comando executado:

```powershell
python scripts/import_colaboradores_json_to_macro_hints.py --json-path "C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\colaboradores.json" --mode Apply --confirm-apply APPLY_COLABORADORES_HINTS
```

Relatorio gerado:

```text
uat_evidence\macro_hints_import\colaboradores_hints_apply_20260603_030554.json
```

Resultado:

- total lido: `111`
- validos: `111`
- criados: `111`
- ignorados: `0`
- invalidos: `0`

Validacoes no banco/API:

- `macro_autocomplete_hints = 111`
- `users = 5`
- `users` permaneceu inalterado pelo Apply de hints
- autocomplete retornou resultados autenticados

## Seguranca e privacidade

- `colaboradores.json` foi usado apenas como hint/autocomplete.
- Nenhum usuario canonico foi criado a partir de `colaboradores.json`.
- Nenhum dado pessoal em massa foi registrado neste documento.
- Nenhum segredo foi impresso ou documentado.
- Apply do `ens.db` nao foi executado.

## Validacoes tecnicas

Comandos executados com sucesso:

```powershell
python -m compileall -q backend/app backend/alembic tests scripts
python -m unittest discover -s tests
ruff check backend tests scripts
cd frontend/itam-platform
npm run build
docker compose config --services
```

Resultado:

- testes Python: `38` executados, `5` skipped, `OK`
- Ruff: `All checks passed`
- frontend build: sucesso
- Docker Compose services: `redis`, `postgres`, `app`

## Riscos restantes

- A validacao visual completa do painel `/macros` em navegador real ainda deve ser feita por QA/UAT.
- O registro de auditoria granular para copia de macro depende do fluxo operacional de uso no frontend.
- O Apply do `ens.db` continua pendente e deve seguir a revisao pre-Apply ja documentada.

## Decisao

Macros oficiais e hints foram aplicados em UAT com sucesso.

O modulo esta pronto para UAT operacional de macros, mantendo `ens.db` fora do Apply desta rodada.
