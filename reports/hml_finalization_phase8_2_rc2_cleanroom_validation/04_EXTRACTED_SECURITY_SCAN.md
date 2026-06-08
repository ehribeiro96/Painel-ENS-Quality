# 04 Extracted Security Scan

- Scan de arquivos proibidos executado sobre a extração limpa.
- Evidência em `evidence/04_extracted_forbidden_scan.txt`.
- Resultado: `NO-GO`.
- Motivo: a extração contém artefatos compilados proibidos no pacote RC2, incluindo `__pycache__` e arquivos `.pyc`.
- Itens permitidos que apareceram e foram classificados como aceitáveis: `config/.env.example`, `infra/hermesops/.env.hml.example` e o namespace legítimo `backend/app/domains/imports/`.
