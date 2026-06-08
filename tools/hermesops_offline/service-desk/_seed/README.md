# Hermes Ops Seed Corpus

Este diretório contém o corpus seed controlado da Fase 2 para Service Desk e Coding.

Objetivos:
- manter documentação técnica sanitizada e validável;
- evitar ingestão cega de dados reais;
- preparar base para sanitização, chunking e futura indexação RAG;
- separar conteúdo por domínio operacional.

Regras desta fase:
- somente conteúdo sanitizado;
- sem senhas, tokens, certificados, chaves privadas ou logs brutos corporativos;
- sem execução automática de scripts administrativos;
- todo documento deve conter front matter YAML obrigatório;
- documentos `restricted` ou `secret` não devem ser enviados a modelos externos.

Comando de sanitização dry-run:

```bash
python3 tools/ingest/sanitize_document.py \
  --input knowledge/service-desk/_seed \
  --output exports/sanitized/phase2_seed \
  --report reports/phase2/sanitization_report.json \
  --dry-run
```

Comando de chunking dry-run:

```bash
python3 tools/ingest/chunk_document.py \
  --input exports/sanitized/phase2_seed \
  --output exports/sanitized/phase2_chunks/chunks.jsonl
```
