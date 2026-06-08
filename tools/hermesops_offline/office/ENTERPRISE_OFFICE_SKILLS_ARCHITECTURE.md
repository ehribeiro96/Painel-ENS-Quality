# Enterprise Office Skills Architecture

## Spreadsheet Skill
Leitura e validacao offline de planilhas sinteticas.

## Word/Docx Skill
Criacao e revisao de documentos editaveis.

## PowerPoint/Pptx Skill
Criacao de decks com narrativa e speaker notes.

## PDF/Adobe Acrobat Skill
PDF como formato final, com cautela para assinatura e redaction.

## Text Editing Skill
Reescrita formal e revisao de tom.

## Fidelidade de arquivos Office e uso controlado do M365

- CSV é apenas formato simples de intercâmbio e staging.
- Quando importam fórmulas, formatação, tabelas, filtros, validações, estilos, layout, múltiplas abas, gráficos, pivots, comentários, proteção ou identidade visual, formatos nativos são preferenciais.
- Formatos principais: .xlsx, .docx, .pptx, .pdf.
- M365/Graph e Office Scripts são HML-gated e não devem conter segredos no Git.
- Office Desktop é fallback interativo e não padrão.
- Adobe Acrobat continua sendo a política padrão para PDF, especialmente para PDF assinado ou sensível.
