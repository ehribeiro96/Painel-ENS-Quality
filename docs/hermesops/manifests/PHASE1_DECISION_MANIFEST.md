# Phase 1 Decision Manifest

## Entra nesta fase

- Documentação raiz do HermesOps
- Governança
- MemoryOS em formato documental
- CoderOS em formato documental
- Enterprise Office Skills em formato documental
- Localization pt-BR
- Políticas Composio read-only
- Documentação Desktop CLI
- Knowledge Service Desk

## Fica isolado

- Desktop patchado runtime
- Electron bridge runtime
- Composio plugin runtime
- HermesOps CLI executável
- Docker Compose HermesOps
- Qdrant/RAG runtime
- Source completo importado

## Bloqueado

- .env
- .env.*
- *.pem
- *.key
- *.pfx
- *.p12
- *.jsonl
- *.log
- venv
- node_modules
- build/dist/release
- runtime logs
- connected accounts
- Composio execute

## Estratégia

Migração seletiva e documental, sem runtime.
