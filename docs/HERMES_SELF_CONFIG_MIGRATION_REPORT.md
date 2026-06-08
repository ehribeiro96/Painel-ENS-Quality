# Relatório de migração da memória pessoal Hermes

Data: 2026-06-05

## Resumo

A memória pessoal de longo prazo foi separada do repositório do Painel ENS-Quality e migrada para:

```text
~/.hermes/estevao_profile/
```

O projeto ficou com documentação em `docs/` e suas ferramentas específicas em `tools/hermes/`.

Gateway não foi iniciado.
Nenhuma nova automação foi criada.
Backend, frontend, banco, migrations, `.env` e `docker-compose.yml` não foram alterados.

## Backup criado antes da movimentação

Backup de segurança criado em:

```text
/home/estevaoqualityadm/.hermes/estevao_profile_backups/pre_move_estevao_profile_20260605_164457.tar.gz
```

Tamanho observado: 24.127 bytes.

Também havia backup anterior desta mesma sessão em:

```text
/home/estevaoqualityadm/.hermes/estevao_profile_backups/pre_migration_estevao_profile_20260605_164341.tar.gz
```

## Itens movidos para o perfil pessoal

Destino base:

```text
/home/estevaoqualityadm/.hermes/estevao_profile/
```

Itens migrados:

| Origem no projeto | Destino pessoal |
|---|---|
| `memory/` | `~/.hermes/estevao_profile/memory/` |
| `projects/` | `~/.hermes/estevao_profile/projects/` |
| `knowledge/` | `~/.hermes/estevao_profile/knowledge/` |
| `playbooks/` | `~/.hermes/estevao_profile/playbooks/` |
| `decisions/` | `~/.hermes/estevao_profile/decisions/` |
| `system/` | `~/.hermes/estevao_profile/system/` |
| `tools/estevao_memory/` | `~/.hermes/estevao_profile/tools/estevao_memory/` |
| `.hermes/estevao_knowledge.sqlite` | `~/.hermes/estevao_profile/cache/estevao_knowledge.sqlite` |
| `.hermes/estevao_knowledge_maintenance.log` | `~/.hermes/estevao_profile/logs/estevao_knowledge_maintenance.log` |
| `audit_report.md` | `~/.hermes/estevao_profile/reports/audit_report.md` |
| `migration_report.md` | `~/.hermes/estevao_profile/reports/migration_report.md` |

## Estrutura atual do perfil pessoal

```text
~/.hermes/estevao_profile/
  README.md
  memory/
  projects/
  knowledge/
  playbooks/
  decisions/
  system/
  tools/estevao_memory/
  cache/estevao_knowledge.sqlite
  logs/estevao_knowledge_maintenance.log
  reports/
```

Contagens validadas:

| Diretório | Arquivos |
|---|---:|
| `memory/` | 5 |
| `projects/` | 4 |
| `knowledge/` | 8 |
| `playbooks/` | 6 |
| `decisions/` | 2 |
| `system/` | 1 |
| `tools/estevao_memory/` | 7 |
| `cache/` | 1 |
| `logs/` | 1 |
| `reports/` | 2 |

## Scripts estabilizados

Foi adicionado o helper:

```text
~/.hermes/estevao_profile/tools/estevao_memory/_paths.py
```

Raiz configurável:

```bash
export ESTEVAO_PROFILE_ROOT="$HOME/.hermes/estevao_profile"
```

Fallback seguro quando a variável não existe:

```text
~/.hermes/estevao_profile
```

Scripts atualizados para usar essa raiz:

- `rag_index.py`
- `rag_search.py`
- `maintenance.py`
- `new_decision.py`
- `new_playbook.py`

Novos destinos internos:

```text
cache/estevao_knowledge.sqlite
logs/estevao_knowledge_maintenance.log
```

## Skill pessoal atualizada

Skill atualizada:

```text
~/.hermes/skills/personal/estevao-long-term-context/SKILL.md
```

Mudanças aplicadas:

- Base pessoal passou a apontar para `~/.hermes/estevao_profile/`.
- Comandos recomendados agora executam a partir do perfil pessoal.
- Referências ao repositório do Painel como base primária foram removidas.
- Foi adicionada fronteira explícita: tarefas do Painel devem seguir `~/projects/Painel-ENS-Quality/HERMES.md`; memória pessoal não deve voltar para a árvore do projeto.

## Script de manutenção Hermes atualizado

Script atualizado:

```text
~/.hermes/scripts/estevao_knowledge_maintenance.py
```

Mudanças aplicadas:

- Usa `ESTEVAO_PROFILE_ROOT` quando definido.
- Usa fallback `~/.hermes/estevao_profile`.
- Executa manutenção com `cwd` no perfil pessoal.
- Grava log em `~/.hermes/estevao_profile/logs/estevao_knowledge_maintenance.log`.
- Não grava mais log/cache no projeto Painel.

O cron job existente continua apontando para o mesmo script:

```text
estevao_knowledge_maintenance.py
```

Nenhuma nova automação foi criada.

## Validação executada

Comando equivalente validado:

```bash
cd ~/.hermes/estevao_profile
ESTEVAO_PROFILE_ROOT=~/.hermes/estevao_profile python3 tools/estevao_memory/rag_index.py
```

Resultado:

```text
indexed_or_updated=0 total_docs=25 db=/home/estevaoqualityadm/.hermes/estevao_profile/cache/estevao_knowledge.sqlite
```

Busca validada:

```bash
python3 tools/estevao_memory/rag_search.py "PowerShell" 3
```

Resultado: retornou documentos de `knowledge/powershell`, `projects/Framework_de_Upgrade_PowerShell` e `memory/identity`.

Manutenção validada:

```bash
python3 tools/estevao_memory/maintenance.py
```

Resultado: execução concluída, índice com 25 documentos e pendências de conteúdo nos arquivos de projetos pessoais.

Script de automação validado manualmente sem gateway:

```bash
python3 ~/.hermes/scripts/estevao_knowledge_maintenance.py
```

Resultado: execução concluída, relatou pendências de conteúdo sem erro.

SQLite validado:

| Tabela | Contagem |
|---|---:|
| `docs` | 25 |
| `docs_fts` | 25 |

## Auditoria de segredos

Após migração, foram escaneados 40 arquivos no perfil pessoal, skill e script de manutenção.

Padrões verificados:

- API keys
- tokens
- senhas/passwords
- Authorization Bearer/Basic
- private keys
- secrets/client secrets

Resultado:

```text
secret_findings_count=0
```

Nenhum valor sensível foi impresso neste relatório.

## Verificação de limpeza no projeto

Itens pessoais ausentes do projeto após a migração:

- `memory/`
- `projects/`
- `knowledge/`
- `playbooks/`
- `decisions/`
- `system/`
- `tools/estevao_memory/`
- `.hermes/estevao_knowledge.sqlite`
- `.hermes/estevao_knowledge_maintenance.log`
- `audit_report.md`
- `migration_report.md`

Itens mantidos no projeto:

- `docs/HERMES_SELF_CONFIG_HARDENING_PLAN.md`
- `docs/HERMES_SELF_CONFIG_MIGRATION_REPORT.md`
- `tools/hermes/`
- `HERMES.md`

## Verificação de paths frágeis

Arquivos ativos verificados:

- scripts em `~/.hermes/estevao_profile/tools/estevao_memory/`
- `~/.hermes/scripts/estevao_knowledge_maintenance.py`
- `~/.hermes/skills/personal/estevao-long-term-context/SKILL.md`

Resultado:

```text
hardcoded_old_project_path_in_active_personal_files=[]
```

Não foi encontrada referência ativa ao path antigo do projeto nos scripts/skill pessoais atualizados.

## Pendências conhecidas

A manutenção aponta conteúdo pendente nos registros pessoais de projetos:

- `projects/ESP-WROOM-32.md`
- `projects/Framework_de_Upgrade_PowerShell.md`
- `projects/Automacao_de_Help_Desk.md`
- `projects/Build_Mod.md`

Essas pendências são de revisão de conteúdo, não de migração.

## Observação sobre cron

O cron job existente foi listado e permanece existente:

- Nome: `Estevão knowledge maintenance`
- Script: `estevao_knowledge_maintenance.py`
- `no_agent`: `true`
- Entrega: `local`

O script chamado por ele foi atualizado para operar no perfil pessoal. Nenhum gateway foi iniciado.

## Critério para considerar a migração concluída

Migração técnica concluída porque:

- Memória pessoal foi retirada da árvore do projeto.
- Perfil pessoal existe e contém a base migrada.
- Scripts usam raiz configurável.
- Skill aponta para o novo perfil.
- Cache/logs foram redirecionados para o perfil pessoal.
- Indexação, busca e manutenção executaram sem erro.
- Auditoria de segredos não encontrou achados nos arquivos escaneados.
- Projeto mantém apenas docs e ferramentas específicas do Painel.

## Próxima revisão recomendada

Revisar manualmente o conteúdo dos arquivos pessoais marcados como pendentes antes de tratá-los como fonte canônica.
