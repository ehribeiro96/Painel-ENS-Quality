# Macros End-to-End UAT Report

## 1. Resumo executivo

Foi executada uma sessao UAT ponta a ponta simulando o uso real do tecnico de TI:

```text
Ativo -> Movimentacao -> Macro gerada -> Macro copiada -> Macro colada em chamado simulado -> Auditoria validada
```

Resultado final: `GO`.

O Apply do `ens.db` nao foi executado. A confirmacao `APPLY_LEGACY_ENS_DB` nao foi usada. A tabela `users` permaneceu com `5` registros.

## 2. Ativo de teste usado

Ativo controlado criado para esta validacao:

| Campo | Valor |
| --- | --- |
| id | `9c13e1df-e690-4c2e-80e4-b320efff6717` |
| hostname | `QA-MACRO-E2E-003851` |
| patrimonio | `PAT-MACRO-E2E-003851` |
| serial | mascarado como `SN-MACRO-E2E-******` |
| tipo | `NOTEBOOK` |
| fabricante/modelo | `Dell Latitude QA` |

Nao foram usados dados pessoais sensiveis.

## 3. Estado antes da movimentacao validada

| Campo | Valor |
| --- | --- |
| status | `STOCK` |
| localizacao | `Bancada QA Macro` |
| usuario atual | `Sem usuario` |

## 4. Dados da movimentacao

Movimentacao criada pela interface `/assets`:

| Campo | Valor |
| --- | --- |
| movement_id | `1b8b7bc5-f141-4818-b327-0936af2dd7f1` |
| status anterior | `STOCK` |
| novo status | `STOCK` |
| local anterior | `Bancada QA Macro` |
| novo local | `Bancada QA Macro 2` |
| usuario anterior | `Sem usuario` |
| usuario atual | `Sem usuario` |
| justificativa | `UAT ponta a ponta macro Service Desk com copia` |

O historico de movimentacao foi criado e o ativo passou a exibir `Bancada QA Macro 2`.

## 5. Macro gerada

Template usado:

```text
ativos-atualizar-inventario
```

Trecho da macro copiada para o chamado simulado:

```text
Atualizar Inventário

Executar atualização de ativos no Lan Sweeper:

Patrimônio: PAT-MACRO-E2E-003851
Unidade: Bancada QA Macro 2
Equipamento: QA-MACRO-E2E-003851 NOTEBOOK Dell Latitude QA
Usuário Anterior: {Usuário Anterior}
Local de: Bancada QA Macro
Usuário Atual: {Usuário Atual}
Local para: Bancada QA Macro 2
Status: STOCK

Atenciosamente,
Service Desk ENS
```

A macro esta legivel e adequada para colagem em chamado de Service Desk.

## 6. Campos preenchidos

Campos preenchidos automaticamente a partir da movimentacao/ativo:

- `Patrimônio`
- `Unidade`
- `Equipamento`
- `Local de`
- `Local para`
- `Status`

## 7. Campos pendentes

Campos pendentes exibidos no modal:

- `Usuário Anterior`
- `Usuário Atual`

Motivo: o ativo estava sem usuario antes e depois da movimentacao. O sistema preservou placeholders pendentes e nao inventou dados.

## 8. Resultado da copia

Validado no navegador:

- botao `Copiar macro` executado;
- feedback visual `Macro copiada` exibido;
- clipboard continha a macro renderizada;
- texto colado em campo de chamado simulado manteve quebras de linha e acentuacao.

## 9. Evidencia de `macro_generations`

Registro gerado:

| Campo | Valor |
| --- | --- |
| generation_id | `16c90f6d-1c51-42ef-ac60-3b91200750b5` |
| context_type | `asset_movement` |
| context_id | `1b8b7bc5-f141-4818-b327-0936af2dd7f1` |
| copied | `true` |
| copied_at | preenchido |
| pending_fields | `["Usuário Anterior", "Usuário Atual"]` |

## 10. Evidencia de `audit_logs`

Eventos confirmados para a movimentacao/geracao:

- `asset_movement_macro_generated`
- `macro_copied`

Eventos globais do modulo tambem ja estavam confirmados em rodada anterior:

- `macro_generated`
- `macro_copied`
- `asset_movement_macro_generated`

Nenhum segredo ou dado sensivel desnecessario foi registrado.

## 11. Problemas encontrados

Durante a primeira tentativa pela UI, a movimentacao foi registrada, mas o modal fechou imediatamente antes de mostrar a macro.

Causa:

- `AssetsPage` chamava `setMovingAsset(null)` logo apos `onMoved`, fechando o `MoveAssetDialog`.

Impacto:

- a macro era gerada pelo backend, mas nao ficava visivel para o tecnico copiar no fluxo operacional.

## 12. Correcoes aplicadas

Correcao pequena aplicada:

- o modal de movimentacao permanece aberto apos salvar;
- a tabela de ativos continua sendo invalidada/atualizada;
- o usuario pode copiar a macro e fechar o modal manualmente.

Arquivo alterado:

- `frontend/itam-platform/src/pages/AssetsPage.tsx`

Nao houve alteracao de schema, regra de movimentacao, usuarios, Lansweeper, assinaturas ou legado.

## 13. Validacoes tecnicas

Comandos executados com sucesso:

```powershell
python -m compileall -q backend/app backend/alembic tests scripts
python -m unittest discover -s tests
ruff check backend tests scripts
cd frontend/itam-platform
npm run build
docker compose config --services
```

Resultados:

- testes Python: `39` executados, `6` skipped, `OK`;
- Ruff: `All checks passed`;
- frontend build: sucesso;
- Docker Compose services: `postgres`, `redis`, `app`.

Rotas confirmadas:

- `GET /health` -> `200`
- `GET /` -> `200`
- `GET /macros` -> `200`
- `GET /assinaturas/` -> `200`
- `GET /admin/` -> `302`
- `GET /api/v1/assets` sem token -> `401`
- `GET /api/v1/macros/templates` sem token -> `401`

## 14. Decisao final

Decisao: `GO`.

Critérios atendidos:

- movimentacao nova criada;
- historico da movimentacao criado;
- macro sugerida gerada;
- template `ativos-atualizar-inventario` usado;
- macro copiada com sucesso;
- `macro_generations` registra geracao e copia;
- `audit_logs` registra eventos esperados;
- `users` permaneceu inalterado;
- Apply do `ens.db` nao foi executado;
- testes, Ruff, build e Compose passaram.

## 15. Proximo passo recomendado

Executar validacao assistida com um tecnico da TI usando um chamado real de teste:

1. selecionar ativo de homologacao;
2. movimentar;
3. copiar macro;
4. colar no chamado;
5. validar texto com o padrao de atendimento do Service Desk;
6. encerrar com evidencia e decisao de piloto.
