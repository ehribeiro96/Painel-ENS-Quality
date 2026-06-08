# Hermes - Painel ENS-Quality

Você é o agente local de desenvolvimento do projeto Painel ENS-Quality.

## Estado atual

O projeto já possui:

- Backend FastAPI modular.
- Frontend React/Vite.
- PostgreSQL como fonte canônica.
- Redis.
- Autenticação JWT/RBAC.
- Auditoria.
- Inventário de ativos.
- Movimentação de ativos.
- Importação Lansweeper.
- Domínio de macros.
- Geração de macro após movimentação parcialmente implementada.
- Portal legado de assinaturas montado em /admin e /assinaturas.

## Objetivo do produto

Evoluir o sistema para o Painel de Controle ENS-Quality:

- Inventário / CMDB operacional.
- Movimentação de ativos.
- Macros automáticas.
- Abertura de chamados ITIL.
- Correção semântica e técnica via IA.
- KCS.
- Qualidade de atendimento.
- Hermes IA interno.

## Prioridade imediata

Corrigir e consolidar o fluxo:

Ativo -> Movimentação -> Macro automática -> Histórico -> Copiar macro

## Regras obrigatórias

1. Não remover legado.
2. Não alterar importação Lansweeper sem pedido explícito.
3. Não alterar autenticação sem plano.
4. Não acessar banco de produção.
5. Não expor segredos.
6. Não criar SQL destrutivo.
7. Não retornar model SQLAlchemy diretamente.
8. Usar DTOs explícitos.
9. Toda alteração persistente deve ter auditoria ou histórico.
10. Macro oficial só pode ser gerada depois da movimentação salva.
11. PostgreSQL é a fonte canônica.
12. IA não deve alterar dados sem preview e aprovação.
13. Não instalar dependências globais do sistema sem necessidade.
14. Para migrations manuais, usar sempre o ambiente virtual do projeto.

## Observação sobre Alembic

Não usar o Alembic instalado via apt para este projeto.

Comando correto:

```bash
cd ~/projects/Painel-ENS-Quality
source .venv/bin/activate
cd backend
python -m alembic upgrade head
cd ..
```

## Ferramentas locais Hermes

Scripts auxiliares ficam em `tools/hermes/` e nao alteram o nucleo do Hermes Agent.

- `tools/hermes/hask`: abre um prompt Markdown no editor e envia para `hermes --cli -t file,code_execution,clarify -z "<prompt>" chat`.
- `tools/hermes/hask tools/hermes/prompts/plan_only.md backend/app`: usa um template existente e adiciona caminhos para o Hermes consultar com `read_file`.
- `tools/hermes/htui`: abre o Hermes TUI sempre na raiz do projeto.
- `tools/hermes/hclip`: envia o clipboard do Windows para o Hermes CLI; falha se o clipboard estiver vazio.
- `tools/hermes/validate-project.sh`: roda compileall, unittest e build do frontend.

Variaveis opcionais:

- `HERMES_EDITOR`: editor usado pelo `hask`.
- `HERMES_PROJECT_ROOT`: raiz do projeto, caso precise sobrescrever o padrao `~/projects/Painel-ENS-Quality`.
