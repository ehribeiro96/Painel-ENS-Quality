# Macros UAT Operational Report

## Objetivo

Validar operacionalmente o modulo de Macros em UAT real, usando navegador e APIs autenticadas, apos o Apply controlado dos templates oficiais e hints do `quality_macros_project`.

O Apply do `ens.db` nao foi executado nesta rodada.

## Ambiente

- Data da validacao: 2026-06-03
- Projeto Docker Compose: `itam_uat`
- URL: `http://127.0.0.1:8080`
- Usuario usado: administrador UAT configurado localmente
- Perfil: `ADMIN`
- Fonte oficial de macros aplicada: `C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\macros.json`
- Fonte oficial de hints aplicada: `C:\Users\estevao.quality\Desktop\Desktop\quality_macros_project\assets\colaboradores.json`

Nenhuma senha, token ou segredo foi registrado neste documento.

## Validacao de rotas

| Rota | Resultado |
| --- | --- |
| `GET /health` | `200` |
| `GET /` | `200` |
| `GET /macros` | `200` |
| `GET /assinaturas/` | `200` |
| `GET /admin/` | `302` |
| `GET /api/v1/macros/templates` sem token | `401` |
| `GET /api/v1/assets` sem token | `401` |

## Pagina `/macros`

Validado em navegador:

- pagina carrega com usuario autenticado;
- lista `7` templates;
- categorias aparecem corretamente:
  - `Suporte`;
  - `Ativos`;
  - `Infraestrutura`;
- busca por `inventário` retorna a macro de ativos;
- filtro por categoria `Ativos` retorna `1` macro;
- template abre corretamente;
- campos obrigatorios aparecem;
- preview renderiza;
- botao copiar funciona;
- feedback `Macro copiada.` aparece apos copiar;
- empty state foi ajustado para referenciar o seed oficial do `quality_macros_project`, sem sugerir fonte obsoleta.

## Templates validados

Templates oficiais presentes:

- `[Suporte] Contato inicial`
- `[Suporte] Resolvido`
- `[Suporte] Continuar atendimento`
- `[Suporte] Agendamento de Prova 0800`
- `[Suporte] Tentativa de contato`
- `[Ativos] Atualizar inventário`
- `[Infraestrutura] Encaminhamento`

## Renderizacao

Validado:

- placeholders preenchidos sao substituidos;
- texto mantem quebras de linha;
- caracteres acentuados aparecem corretamente;
- campos obrigatorios ausentes retornam erro funcional;
- nao houve erro `500` no fluxo validado;
- templates continuam tratados como texto, sem `eval` ou `exec`.

## Autocomplete

Validado:

- hints de colaboradores aparecem em campos como `Nome`, `Usuário Atual` e `Usuário Anterior`;
- busca por `Jose` retornou `3` hints;
- busca por `José` retornou `3` hints;
- busca com e sem acento foi normalizada;
- `users` permaneceu inalterado:
  - antes: `5`;
  - depois: `5`.

`colaboradores.json` continua sendo hint/autocomplete, nao fonte canonica de usuarios.

## Macro `[Ativos] Atualizar inventário`

Validado:

- slug `ativos-atualizar-inventario` existe;
- macro aparece em `/macros`;
- campos esperados aparecem:
  - `Patrimônio`;
  - `Unidade`;
  - `Equipamento`;
  - `Usuário Anterior`;
  - `Local de`;
  - `Usuário Atual`;
  - `Local para`;
  - `Status`;
- preview funciona com dados manuais;
- copiar funciona.

## Macro de movimentacao

Movimento existente usado na validacao:

```text
312dca3b-ce95-4194-b14c-0baf20344ff4
```

Endpoint validado:

```text
GET /api/v1/movements/{movement_id}/suggested-macro
```

Resultado:

- template retornado: `[Ativos] Atualizar inventário`;
- texto renderizado retornado;
- pendencias retornadas:
  - `Usuário Anterior`;
  - `Usuário Atual`;
- nenhum erro `500`;
- macro nao alterou ativo, historico ou usuario.

Ajuste aplicado:

- o modal de movimentacao agora exibe campos pendentes antes da copia;
- o botao de copia mostra feedback visual;
- placeholders pendentes permanecem visiveis para revisao humana.

## Auditoria

Validacao atualizada em 2026-06-03:

- geracao visual em `/macros` cria registro em `macro_generations`;
- copia visual em `/macros` marca `copied=true` e preenche `copied_at`;
- macro sugerida por movimentacao cria registro com `context_type=asset_movement`;
- `context_id` referencia o `movement_id`;
- placeholders pendentes ficam registrados em `input_values._metadata.pending_fields`;
- copia da macro de movimentacao marca a geracao como copiada;
- nenhum segredo ou dado sensivel desnecessario foi registrado.

Eventos confirmados em `audit_logs.after.event`:

- `macro_generated`;
- `macro_copied`;
- `asset_movement_macro_generated`.

## Responsividade

Validado no navegador:

| Viewport | Resultado |
| --- | --- |
| `1920x1080` | sem overflow horizontal |
| `1366x768` | sem overflow horizontal |
| aproximacao de zoom `125%` | sem overflow horizontal |

O preview em textarea permaneceu usavel e preservou quebras de linha.

## Problemas corrigidos

1. Autocomplete nao estava conectado ao painel de macros.
   - Correcao: campos `Nome`, `Usuário Atual` e `Usuário Anterior` passaram a usar hints reais de `macro_autocomplete_hints`.

2. Busca de autocomplete nao era normalizada para acento/sem acento.
   - Correcao: query do backend passou a ser normalizada antes do filtro.

3. Botao copiar nao dava feedback visual.
   - Correcao: exibicao de `Macro copiada.` apos copiar.

4. Macro sugerida de movimentacao nao destacava campos pendentes.
   - Correcao: pendencias retornadas pelo backend agora aparecem no modal.

5. Empty state citava seed generico.
   - Correcao: mensagem passou a orientar verificacao da fonte oficial `quality_macros_project`.

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

Resultados:

- testes Python: `39` executados, `5` skipped, `OK`;
- Ruff: `All checks passed`;
- frontend build: sucesso;
- Docker Compose services: `redis`, `postgres`, `app`.

## Riscos restantes

- O fluxo de movimentacao foi validado com movimento existente; uma movimentacao nova completa deve ser exercitada por usuario UAT em sessao controlada.
- Apply do `ens.db` continua pendente e fora desta rodada.

## Atualizacao UX 2026-06-03

Foi aplicada uma rodada conservadora de UX na tela `/macros`:

- preview vazio passou a orientar o usuario a preencher campos e gerar preview;
- campos obrigatorios receberam marcador visual;
- pendencias aparecem em alerta e chips;
- macro `ativos-atualizar-inventario` ficou identificada como usada em movimentacoes de ativos.

Nao houve alteracao de regra de macro, auditoria, banco ou importacao.

## Decisao

Decisao: `GO`.

Justificativa:

- `/macros` esta funcional;
- as `7` macros oficiais aparecem;
- macro `[Ativos] Atualizar inventário` renderiza;
- autocomplete funciona sem criar usuarios;
- macro sugerida de movimentacao funciona;
- placeholders pendentes estao visiveis;
- copiar macro funciona;
- auditoria granular de geracao/copia/movimentacao existe;
- nao houve erro `500`;
- testes, Ruff, build e Compose passaram;
- Apply do `ens.db` nao foi executado.
