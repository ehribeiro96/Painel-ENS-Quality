# Runtime Fixes Report

Data: 2026-06-02

## Correcoes preservadas nesta rodada

- `IntegrityError` tratado como HTTP 409 em operacoes transacionais.
- Filtro operacional `without_user=true` mantido para o card "Sem usuario".
- Apply parcial de importacao preservado com isolamento por linha.
- SignaturesPage continua usando o client HTTP central.
- `starlette` declarado como dependencia direta do backend.
- NGINX opcional aponta para `app:8080`.

## Ajustes UX/UI

- Sidebar e navegacao alinhadas aos prints.
- Dashboard reorganizado com cards e paineis usando dados reais.
- `Usuarios` renomeado na UI para `Colaboradores`.
- Criada visao `Atribuicoes` a partir de ativos atualmente vinculados.
- Auditoria e Importar/Exportar tiveram microcopy/tabelas ajustadas.

## Fora de escopo

- API Lansweeper.
- IA.
- Novos status operacionais.
- Reescrita backend/frontend.
- Remocao do legado Flask.
