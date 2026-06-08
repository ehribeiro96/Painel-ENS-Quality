# M365 Office Integration Plan

## Excel
- workbook em SharePoint/OneDrive
- tabelas estruturadas
- Office Scripts
- Graph Excel API

## Word
- documentos docx em SharePoint/OneDrive
- Graph para armazenamento
- Open XML para manipulacao

## PowerPoint
- pptx em SharePoint/OneDrive
- Graph para armazenamento
- Open XML para manipulacao

## PDF
- PDFs finais em SharePoint/OneDrive
- Acrobat como ferramenta padrao
- Adobe PDF Services futura

## Fidelidade de arquivos Office e uso controlado do M365

- CSV é apenas formato simples de intercâmbio e staging.
- Quando importam fórmulas, formatação, tabelas, filtros, validações, estilos, layout, múltiplas abas, gráficos, pivots, comentários, proteção ou identidade visual, formatos nativos são preferenciais.
- Formatos principais: .xlsx, .docx, .pptx, .pdf.
- M365/Graph e Office Scripts são HML-gated e não devem conter segredos no Git.
- Office Desktop é fallback interativo e não padrão.
- Adobe Acrobat continua sendo a política padrão para PDF, especialmente para PDF assinado ou sensível.
