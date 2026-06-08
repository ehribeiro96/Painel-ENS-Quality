# MemoryOS Consolidation Rules

## Pesquisa vira candidato, não verdade

Toda pesquisa deve entrar primeiro em `memory/inbox/research_candidates/`.

Só pode virar memória aprovada após revisão de fonte, classificação, sanitização, ausência de segredo, aplicabilidade ao HermesOps, avaliação de validade temporal, checagem de conflito e validação humana quando necessário.

## Fato, inferência e decisão

- `facts`: aquilo que a fonte sustenta.
- `inferences`: conclusão do Hermes baseada em fatos.
- `decisions`: escolha operacional tomada no projeto.

## O que nunca entra como memória aprovada

- segredo
- token
- certificado
- PFX/P12
- senha
- `.env`
- dado pessoal desnecessário
- PDF real sensível
- documento jurídico real
- log real não sanitizado
- inventário bruto
- comando destrutivo sem validação
- recomendação sem fonte
- conteúdo contraditório sem resolução

## Validação

- Fonte registrada
- Sensibilidade definida
- Risco definido
- Revisão humana quando procedural

## Rollback

- Rejeitar candidato e registrar motivo em `memory/rejected/`.
