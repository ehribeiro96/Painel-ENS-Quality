# Spreadsheet Skill Spec

## Escopo
- ler xlsx, csv e json sinteticos
- validar colunas e tipos
- detectar valores ausentes e duplicidade
- padronizar tabelas
- gerar relatorios de qualidade
- preparar payloads para Excel/M365

## Relacoes
- PowerPoint: dados limpos podem virar graficos e tabelas
- PDF: exportacao final futura via Acrobat com revisao humana

## Fidelidade de arquivos Office e uso controlado do M365

- CSV é apenas formato simples de intercâmbio e staging.
- Quando importam fórmulas, formatação, tabelas, filtros, validações, estilos, layout, múltiplas abas, gráficos, pivots, comentários, proteção ou identidade visual, formatos nativos são preferenciais.
- Formatos principais: .xlsx, .docx, .pptx, .pdf.
- M365/Graph e Office Scripts são HML-gated e não devem conter segredos no Git.
- Office Desktop é fallback interativo e não padrão.
- Adobe Acrobat continua sendo a política padrão para PDF, especialmente para PDF assinado ou sensível.
