# Hardening da self-configuration Hermes

Data da auditoria: 2026-06-05
Escopo: estrutura de memória/contexto criada dentro do repositório `Painel-ENS-Quality`, skill pessoal Hermes e automação Hermes existente.

## Restrições respeitadas nesta etapa

- Gateway não iniciado.
- Gateway não instalado.
- Nenhum arquivo apagado.
- Nenhum arquivo movido.
- `.env` não alterado.
- `docker-compose.yml` não alterado.
- Backend/frontend do Painel não alterados.
- Banco/migrations do Painel não alterados.
- Nenhum segredo foi gravado neste relatório.
- Nenhum valor sensível foi impresso.
- Nenhuma nova automação criada.
- Cron existente apenas listado/auditado; não foi alterado.
- Hermes não foi atualizado.
- `package-lock.json` do Hermes não foi tocado.
- Conteúdos de projetos pessoais foram tratados como não verificados quando não havia fonte externa no escopo.

## 1. Inventário dos arquivos criados

### Raiz do projeto

| Item | Tipo | Existe | Tamanho/contagem | Observação |
|---|---:|---:|---:|---|
| `audit_report.md` | arquivo | sim | 2.929 bytes | relatório de auditoria inicial |
| `migration_report.md` | arquivo | sim | 2.644 bytes | relatório de migração inicial |
| `memory/` | diretório | sim | 5 arquivos | memória pessoal declarativa |
| `projects/` | diretório | sim | 4 arquivos | registros de projetos pessoais/recorrentes |
| `knowledge/` | diretório | sim | 8 arquivos | base técnica genérica por domínio |
| `playbooks/` | diretório | sim | 6 arquivos | procedimentos reutilizáveis/modelos |
| `decisions/` | diretório | sim | 2 arquivos | decisões e template |
| `system/` | diretório | sim | 1 arquivo | prompt/contexto sistêmico pessoal |
| `tools/estevao_memory/` | diretório | sim | 6 arquivos | ferramentas locais de indexação/criação |
| `.hermes/estevao_knowledge.sqlite` | arquivo | sim | 65.536 bytes | índice/cache SQLite FTS5 |

### Conteúdo de `memory/`

- `memory/career.md`
- `memory/decision_patterns.md`
- `memory/identity.md`
- `memory/personality.md`
- `memory/preferences.md`

### Conteúdo de `projects/`

- `projects/Automacao_de_Help_Desk.md`
- `projects/Build_Mod.md`
- `projects/ESP-WROOM-32.md`
- `projects/Framework_de_Upgrade_PowerShell.md`

### Conteúdo de `knowledge/`

- `knowledge/python/README.md`
- `knowledge/helpdesk/README.md`
- `knowledge/troubleshooting/README.md`
- `knowledge/windows/README.md`
- `knowledge/linux/README.md`
- `knowledge/powershell/README.md`
- `knowledge/networking/README.md`
- `knowledge/automation/README.md`

### Conteúdo de `playbooks/`

- `playbooks/TEMPLATE.md`
- `playbooks/deploy_7zip.md`
- `playbooks/deploy_acrobat.md`
- `playbooks/deploy_firefox.md`
- `playbooks/deploy_klite.md`
- `playbooks/deploy_zoom.md`

### Conteúdo de `decisions/`

- `decisions/2026-06-05_estrutura_memoria_hermes.md`
- `decisions/TEMPLATE.md`

### Conteúdo de `system/`

- `system/estevao_system_prompt.md`

### Conteúdo de `tools/estevao_memory/`

- `tools/estevao_memory/README.md`
- `tools/estevao_memory/maintenance.py`
- `tools/estevao_memory/new_decision.py`
- `tools/estevao_memory/new_playbook.py`
- `tools/estevao_memory/rag_index.py`
- `tools/estevao_memory/rag_search.py`

### Skill pessoal

- `~/.hermes/skills/personal/estevao-long-term-context/SKILL.md`
- Existe.
- Tamanho auditado: 3.203 bytes.
- Função: skill pessoal para carregar preferências, critérios de decisão, base local e comandos de busca/indexação.

### Script de automação Hermes

- `~/.hermes/scripts/estevao_knowledge_maintenance.py`
- Existe.
- Tamanho auditado: 1.051 bytes.
- Função observada: chama `tools/estevao_memory/maintenance.py`, grava log em `.hermes/estevao_knowledge_maintenance.log` dentro do projeto e só imprime saída quando encontra pendências.

### Cron job Hermes existente

- Nome: `Estevão knowledge maintenance`
- ID observado: `da2f5bb77119`
- Agenda: `0 8 * * 1`
- Repetição: indefinida
- Entrega: `local`
- Estado: habilitado/agendado
- `no_agent`: `true`
- Script: `estevao_knowledge_maintenance.py`
- Última execução observada: nenhuma registrada no momento da auditoria
- Nenhuma alteração foi aplicada ao cron.

## 2. Classificação

| Item | Classificação primária | Classificação secundária | Fora de lugar? | Justificativa |
|---|---|---|---:|---|
| `audit_report.md` | relatório | contexto de self-configuração | sim, parcialmente | relatório sobre configuração pessoal dentro do repositório do Painel |
| `migration_report.md` | relatório | contexto de self-configuração | sim, parcialmente | relatório de migração pessoal dentro do repositório do Painel |
| `memory/` | memória pessoal | contexto de longo prazo | sim | contém identidade, preferências, carreira e padrões decisórios pessoais |
| `projects/` | memória pessoal | contexto de projetos pessoais/recorrentes | sim | registra projetos não necessariamente pertencentes ao Painel ENS-Quality |
| `knowledge/` | memória pessoal/técnica | base reutilizável | sim, salvo se houver subconteúdo específico do Painel | domínios genéricos como Python, PowerShell, Windows e networking não pertencem ao código do Painel |
| `playbooks/` | ferramenta/conhecimento reutilizável | memória operacional | sim, parcialmente | playbooks pessoais de suporte/deploy não são artefatos do produto Painel, salvo se documentarem operação do próprio Painel |
| `decisions/` | memória pessoal | decisões de self-configuração | sim | decisões sobre estrutura Hermes pessoal não pertencem ao domínio funcional do Painel |
| `system/` | memória pessoal | prompt/contexto pessoal | sim | prompt pessoal de operação do assistente não é documentação do Painel |
| `tools/estevao_memory/` | ferramenta reutilizável | tooling Hermes local | sim, parcialmente | ferramentas são úteis, mas acopladas ao repositório atual; deveriam ficar sob perfil pessoal ou, se mantidas no projeto, em `tools/hermes/` somente para ferramentas do Painel |
| `.hermes/estevao_knowledge.sqlite` | índice/cache | derivado de memória pessoal | sim | cache gerado não deve residir no repositório do produto |
| skill pessoal | memória pessoal/Hermes skill | ponto de entrada contextual | não quanto ao local, sim quanto às referências | localização em `~/.hermes/skills/personal/` é adequada; referências internas apontam para base pessoal dentro do projeto |
| script de automação | automação | manutenção de índice/cache | não quanto ao local, sim quanto ao alvo | localização em `~/.hermes/scripts/` é aceitável; alvo hardcoded aponta para o projeto |
| cron job | automação | manutenção agendada | não quanto ao mecanismo, sim quanto ao alvo atual | cron existe no Hermes, mas executa manutenção de memória pessoal dentro do repo do Painel |

## 3. Riscos encontrados

### Separação de responsabilidades

Risco alto de mistura entre:

- memória pessoal de longo prazo;
- documentação técnica do produto Painel ENS-Quality;
- scripts reutilizáveis do Hermes;
- índice/cache derivado.

Impacto: contaminação do repositório com contexto pessoal, risco de commit acidental, dificuldade de distinguir documentação oficial do produto de memória operacional pessoal.

### Paths frágeis

Foram detectadas referências absolutas/hardcoded ao ambiente atual em:

- `audit_report.md`
- `migration_report.md`
- `~/.hermes/skills/personal/estevao-long-term-context/SKILL.md`
- `~/.hermes/scripts/estevao_knowledge_maintenance.py`

Risco: a estrutura quebra se o projeto mudar de diretório, se outro perfil Hermes for usado, se o usuário mudar de máquina ou se a base pessoal for separada corretamente.

### Scripts acoplados ao repositório atual

Os scripts em `tools/estevao_memory/` calculam a raiz por `Path(__file__).resolve().parents[2]`. Isso funciona enquanto eles estão dentro de:

`~/projects/Painel-ENS-Quality/tools/estevao_memory/`

Mas não existe suporte observado para variável de ambiente como `ESTEVAO_PROFILE_ROOT`.

Risco: mover a base pessoal futuramente sem ajustar os scripts quebra indexação, busca, criação de decisões e criação de playbooks.

### Cron/hook perigoso

Não foi observado comando destrutivo no script de cron auditado.

O cron é `no_agent=true`, chama Python local e tem timeout de 120 segundos no wrapper. Isso reduz risco de execução autônoma aberta. Porém, o alvo atual é inadequado: mantém índice/log de memória pessoal dentro do repositório do Painel.

### Conteúdo genérico ou pendente

Foram detectados termos indicativos de placeholder/pendência em múltiplos arquivos, especialmente:

- `projects/*.md`
- `knowledge/troubleshooting/README.md`
- `playbooks/deploy_*.md`
- `tools/estevao_memory/maintenance.py`
- `tools/estevao_memory/new_decision.py`
- relatórios iniciais

Isso não prova conteúdo inventado, mas indica necessidade de revisão manual antes de tratar como fonte canônica.

### Possível falso positivo em binário SQLite

A varredura textual bruta do arquivo `.hermes/estevao_knowledge.sqlite` encontrou um padrão que parece comando destrutivo, mas por se tratar de binário/cache SQLite o resultado deve ser tratado como possível falso positivo. A inspeção estrutural mostrou tabelas FTS5 esperadas (`docs`, `docs_fts` e auxiliares), com 25 documentos indexados.

### Risco de commit acidental

A presença de `.hermes/estevao_knowledge.sqlite`, memória pessoal e relatórios na árvore do projeto aumenta risco de versionar material pessoal/caches se `.gitignore` não cobrir esses caminhos. Esta auditoria não alterou `.gitignore`; recomenda-se revisar em etapa futura.

## 4. Segredos detectados, sem imprimir valores

Resultado da varredura local por padrões de:

- API keys;
- tokens;
- senhas/senhas em português;
- `Authorization: Bearer` / `Authorization: Basic`;
- private keys;
- `secret` / `client_secret`.

Nenhum segredo foi detectado pelos padrões aplicados nos arquivos auditados.

Limitação: isso não substitui revisão manual nem ferramenta dedicada de secret scanning. Recomenda-se rodar scanner específico em etapa futura antes de qualquer commit/migração.

## 5. O que deve ficar no projeto

Destino projeto permitido:

- `~/projects/Painel-ENS-Quality/docs/`
- `~/projects/Painel-ENS-Quality/tools/hermes/`
- `~/projects/Painel-ENS-Quality/HERMES.md`

Deve ficar no projeto somente o que for específico do Painel ENS-Quality:

1. `docs/HERMES_SELF_CONFIG_HARDENING_PLAN.md`
   - Este arquivo deve permanecer como registro de hardening e plano de separação.

2. `HERMES.md`
   - Deve continuar contendo apenas contexto operacional do projeto Painel, regras de segurança, comandos locais e prioridades do produto.
   - Não deve incorporar memória pessoal longa, projetos pessoais, preferências detalhadas nem base KCS pessoal.

3. `tools/hermes/`
   - Deve conter apenas scripts auxiliares relacionados ao uso do Hermes dentro do projeto Painel.
   - Ferramentas pessoais de memória devem sair de `tools/estevao_memory/` futuramente ou ser substituídas por wrappers de projeto que apontem para o perfil pessoal.

4. `docs/`
   - Pode conter documentação técnica do Painel, decisões do Painel, planos do Painel e relatórios de auditoria do Painel.
   - Não deve conter identidade pessoal, carreira, preferências pessoais ou projetos externos.

## 6. O que deve ir para `~/.hermes/estevao_profile`

Destino pessoal recomendado:

`~/.hermes/estevao_profile/`

Estrutura proposta:

```text
~/.hermes/estevao_profile/
  README.md
  memory/
  projects/
  knowledge/
  playbooks/
  decisions/
  system/
  tools/
    estevao_memory/
  cache/
    estevao_knowledge.sqlite
  logs/
    estevao_knowledge_maintenance.log
  reports/
    audit_report.md
    migration_report.md
```

Itens que devem migrar para esse destino pessoal em etapa futura:

- `memory/`
- `projects/`
- `knowledge/`
- `playbooks/`
- `decisions/`
- `system/`
- `.hermes/estevao_knowledge.sqlite`
- `.hermes/estevao_knowledge_maintenance.log`, se existir
- `tools/estevao_memory/`, após ajuste para raiz configurável
- `audit_report.md`, se for relatório da base pessoal e não do Painel
- `migration_report.md`, se for relatório da base pessoal e não do Painel

A skill `~/.hermes/skills/personal/estevao-long-term-context/SKILL.md` deve continuar em `~/.hermes/skills/personal/`, mas precisa ser revisada futuramente para apontar para `~/.hermes/estevao_profile/` e não para o repositório do Painel.

O script `~/.hermes/scripts/estevao_knowledge_maintenance.py` pode continuar em `~/.hermes/scripts/`, mas deve ser ajustado futuramente para resolver a raiz por `ESTEVAO_PROFILE_ROOT` com fallback seguro.

## 7. O que deve ser revisado manualmente

Revisar manualmente antes de considerar canônico:

1. `projects/*.md`
   - Confirmar se os projetos listados existem, se os estados estão corretos e se não há inferências inventadas.

2. `playbooks/deploy_*.md`
   - Validar comandos, pré-requisitos, permissões, rollback e riscos.
   - Não tratar como procedimento aprovado até revisão.

3. `knowledge/*/README.md`
   - Separar conhecimento real, genérico, incompleto e placeholders.

4. `memory/*.md`
   - Confirmar se preferências, identidade, carreira e padrões decisórios refletem fatos estáveis e úteis.
   - Remover ou corrigir qualquer extrapolação.

5. `system/estevao_system_prompt.md`
   - Garantir que não contenha instruções que conflitem com regras de segurança do projeto ou do Hermes.

6. `decisions/2026-06-05_estrutura_memoria_hermes.md`
   - Validar decisão como registro pessoal, não como decisão arquitetural do Painel.

7. Skill pessoal
   - Remover referência ao projeto como “Primary local base”.
   - Substituir comandos por comandos baseados em raiz configurável.

8. Cron existente
   - Revisar depois da migração para garantir que a manutenção rode sobre `~/.hermes/estevao_profile/`, não sobre o projeto.

9. `.gitignore`
   - Em etapa futura, verificar se memória pessoal, caches SQLite e logs estão protegidos contra commit acidental.

## 8. Plano de migração seguro

Nenhuma movimentação deve ocorrer antes da revisão manual e antes de confirmar backup.

Plano recomendado para etapa futura:

1. Criar backup não destrutivo.
   - Arquivar os diretórios/arquivos atuais para um `.tar.gz` local fora do repositório ou sob área temporária segura.
   - Não remover originais.

2. Criar `~/.hermes/estevao_profile/`.
   - Criar subpastas `memory`, `projects`, `knowledge`, `playbooks`, `decisions`, `system`, `tools`, `cache`, `logs`, `reports`.

3. Copiar, não mover, a base pessoal.
   - Copiar `memory/`, `projects/`, `knowledge/`, `playbooks/`, `decisions/`, `system/` para o perfil pessoal.
   - Copiar `tools/estevao_memory/` para `~/.hermes/estevao_profile/tools/estevao_memory/`.
   - Copiar relatórios pessoais para `reports/`.
   - Copiar ou regenerar o SQLite em `cache/`.

4. Ajustar scripts em etapa futura, ainda sem apagar origem.
   - Introduzir `ESTEVAO_PROFILE_ROOT`.
   - Usar fallback explícito para `Path.home() / ".hermes" / "estevao_profile"`.
   - Evitar inferir raiz pelo caminho do arquivo quando o script puder ser chamado de múltiplos locais.

5. Regenerar índice no novo destino.
   - Validar contagem de documentos indexados.
   - Comparar resultado com o índice antigo.

6. Atualizar skill pessoal.
   - Trocar referências do repositório do Painel para `~/.hermes/estevao_profile/`.
   - Manter instrução para consultar `HERMES.md` quando a tarefa for especificamente sobre o Painel.

7. Atualizar script do cron existente.
   - O cron em si não precisa ser recriado.
   - O script chamado pelo cron deve passar a usar raiz configurável.
   - Só alterar o cron se o nome do script ou estratégia de execução realmente mudar.

8. Rodar validação local sem gateway.
   - Executar indexação manual.
   - Executar busca manual.
   - Executar manutenção manual.
   - Confirmar que nenhum arquivo novo é escrito no repositório do Painel, exceto documentação deliberada.

9. Depois de validado, decidir limpeza.
   - Somente após backup, validação e aprovação manual, decidir se os arquivos pessoais antigos serão removidos do repositório.
   - Esta etapa não deve ser automática.

## 9. Ordem recomendada de execução

1. Revisão manual deste relatório.
2. Secret scan dedicado em toda a árvore envolvida.
3. Revisão factual dos conteúdos pessoais/projetos/playbooks.
4. Criar backup.
5. Criar `~/.hermes/estevao_profile/`.
6. Copiar dados pessoais para o novo destino.
7. Implementar suporte a `ESTEVAO_PROFILE_ROOT` nos scripts.
8. Regenerar índice no novo destino.
9. Testar `rag_index.py`, `rag_search.py`, `maintenance.py`, `new_decision.py` e `new_playbook.py` no novo destino.
10. Atualizar skill pessoal para apontar para o novo perfil.
11. Ajustar script de automação existente para usar o novo perfil.
12. Rodar manutenção manual sem gateway.
13. Revisar logs e garantir ausência de segredos/paths indevidos.
14. Revisar `.gitignore` do projeto para impedir commit acidental de caches/memória pessoal.
15. Só então avaliar remoção/movimentação definitiva dos arquivos antigos, mediante aprovação explícita.

## 10. Critério para só então iniciar gateway

Gateway só deve ser iniciado depois que todos os critérios abaixo forem cumpridos:

- Base pessoal separada fisicamente em `~/.hermes/estevao_profile/`.
- Skill pessoal apontando para o perfil pessoal, não para o repositório do Painel.
- Scripts aceitando `ESTEVAO_PROFILE_ROOT` ou usando fallback seguro para `~/.hermes/estevao_profile/`.
- Cron existente validado para não escrever memória/cache/logs dentro do projeto Painel.
- Secret scan dedicado concluído sem achados críticos.
- Conteúdo pessoal revisado manualmente para remover placeholders, extrapolações e conteúdo inventado.
- `.gitignore` ou política equivalente protegendo caches/logs/memória pessoal contra commit acidental.
- Execução manual de indexação, busca e manutenção concluída sem alterar backend/frontend/banco/migrations do Painel.
- Nenhum arquivo `.env`, `docker-compose.yml`, migration ou código de aplicação alterado por esse processo.

## 11. Nota de maturidade revisada

Maturidade atual: protótipo funcional, mas acoplado ao repositório errado.

Avaliação:

- Funcionalidade: média. A base é indexável, pesquisável e tem manutenção agendada.
- Segurança: média-baixa. Nenhum segredo foi detectado, mas há risco operacional por mistura com repositório de produto e paths absolutos.
- Manutenibilidade: baixa-média. Scripts simples e compreensíveis, porém acoplados à posição atual na árvore.
- Separação de contexto: baixa. Memória pessoal, tooling e cache estão dentro do Painel ENS-Quality.
- Prontidão para gateway: insuficiente. Não iniciar gateway enquanto a separação não estiver concluída e validada.

Nota revisada: 5/10.

Justificativa: a implementação inicial tem valor como prova de conceito, mas ainda não atende a isolamento, portabilidade e higiene operacional necessários para uso contínuo. O próximo marco de maturidade é separar o perfil pessoal, parametrizar raiz por `ESTEVAO_PROFILE_ROOT`, validar conteúdo e impedir escrita acidental no repositório do Painel.

## Observação específica sobre `ESTEVAO_PROFILE_ROOT`

Verificação dos scripts em `tools/estevao_memory/`:

| Script | Aceita `ESTEVAO_PROFILE_ROOT` hoje? | Observação |
|---|---:|---|
| `maintenance.py` | não | usa raiz inferida por `Path(__file__).resolve().parents[2]` |
| `new_decision.py` | não | usa raiz inferida por `Path(__file__).resolve().parents[2]` |
| `new_playbook.py` | não | usa raiz inferida por `Path(__file__).resolve().parents[2]` |
| `rag_index.py` | não | usa raiz inferida por `Path(__file__).resolve().parents[2]`; grava DB em `.hermes/estevao_knowledge.sqlite` sob essa raiz |
| `rag_search.py` | não | usa raiz inferida por `Path(__file__).resolve().parents[2]`; lê DB em `.hermes/estevao_knowledge.sqlite` sob essa raiz |

Ajuste futuro recomendado, sem aplicar patch nesta etapa:

```python
import os
from pathlib import Path

ROOT = Path(os.environ.get("ESTEVAO_PROFILE_ROOT", Path.home() / ".hermes" / "estevao_profile")).expanduser().resolve()
```

Para cache/logs, preferir:

```python
DB = ROOT / "cache" / "estevao_knowledge.sqlite"
LOG = ROOT / "logs" / "estevao_knowledge_maintenance.log"
```

Essa mudança deve ser aplicada depois de copiar a base para o novo destino e antes de reabilitar qualquer fluxo automatizado dependente da nova estrutura.
