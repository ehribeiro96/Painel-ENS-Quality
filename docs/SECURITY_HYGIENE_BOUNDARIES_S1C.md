# S1-C — Security/Hygiene Boundaries

## 1. Resumo
- Status: aplicada a fronteira de hygiene
- Escopo: `.gitignore`, `.dockerignore`
- Arquivos alterados: `.gitignore`, `.dockerignore`, `docs/SECURITY_HYGIENE_BOUNDARIES_S1C.md`, `docs/TRACKED_HYGIENE_CANDIDATES_S1C.txt`
- Arquivos não alterados: código, runtime, docs de conteúdo, segredos e artefatos existentes

## 2. Contexto
- Baseado na S1-B.
- Total de hits analisados: 1613.
- Segredos reais confirmados: 0.
- Rotação confirmada: 0.

## 3. Alterações aplicadas
### .gitignore
- Padrões adicionados:
  - `logs/`
  - `reports/`
  - `evidence/`
  - `data/previews/`
  - padrões para segredos locais, dumps, backups e artefatos de token/secret
- Padrões preservados:
  - exemplos de `.env`
  - ignore de caches, build artefatos e dependências locais
  - `imports/HermesOps-Final-Transfer/current`
  - `imports/HermesOps-Final-Transfer/releases/`
- Padrões deliberadamente não adicionados:
  - `docs/` inteiro
  - `assets/` inteiro
  - `tools/` inteiro
  - `imports/` inteiro

### .dockerignore
- Padrões adicionados:
  - `logs/`
  - `reports/`
  - `evidence/`
  - `data/previews/`
  - padrões para segredos locais, dumps, backups e artefatos de token/secret
- Padrões preservados:
  - allowlist de `docs/audit/`
  - exclusão de `.git/`, `.github/`, `node_modules/` e dependências locais
- Padrões deliberadamente não adicionados:
  - `docs/` como árvore inteira sem allowlist
  - `assets/` inteiro
  - `tools/` inteiro

## 4. Arquivos tracked que exigem decisão futura
Ver `docs/TRACKED_HYGIENE_CANDIDATES_S1C.txt`.

## 5. Fora de escopo nesta fase
- Sanitização de docs/examples.
- Remoção do índice Git.
- Rotação de segredos.
- Alteração de scripts.
- Alteração runtime.

## 6. Próximas fases
- S1-D: sanitizar docs/examples.
- S1-E: remover artefatos locais do índice Git, se confirmado.
- S1-F: rotação se segredo real for confirmado.
- S1-G: clean-room/release validation.

## 7. GO/NO-GO
- S1-C: GO
- Release geral: NO-GO
- D2 Desktop oficial: GO em paralelo, desde que não dependa de higiene/release
