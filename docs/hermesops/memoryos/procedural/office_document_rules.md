# office_document_rules.md

Procedural memory rule set with human review requirement.

## Escopo
- Office docs are artifacts, not automatic truth.
- PDF signed or sensitive content requires caution.
- M365/Graph stays HML-gated.

## Validação
- Offline only
- Dados sintéticos
- Revisão humana quando aplicável

## Riscos
- Memória ou classificação incorreta se a fonte for fraca
- Conflitos precisam revisão humana

## Rollback
- Remover candidatos inválidos e registrar motivo

## Fidelidade de arquivos Office e uso controlado do M365

- CSV é apenas formato simples de intercâmbio e staging.
- Quando importam fórmulas, formatação, tabelas, filtros, validações, estilos, layout, múltiplas abas, gráficos, pivots, comentários, proteção ou identidade visual, formatos nativos são preferenciais.
- Formatos principais: .xlsx, .docx, .pptx, .pdf.
- M365/Graph e Office Scripts são HML-gated e não devem conter segredos no Git.
- Office Desktop é fallback interativo e não padrão.
- Adobe Acrobat continua sendo a política padrão para PDF, especialmente para PDF assinado ou sensível.

## pt-BR
- pt-BR é o idioma padrão de resposta operacional do HermesOps, salvo quando o usuário pedir outro idioma ou quando a sintaxe técnica exigir preservação em inglês.
- Relatórios e instruções Office devem priorizar fidelidade documental e linguagem clara.
- Preservar nomes oficiais de produtos, fórmulas e mensagens originais.
