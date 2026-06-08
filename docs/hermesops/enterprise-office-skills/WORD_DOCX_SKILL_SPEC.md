# Word/Docx Skill Spec

## Escopo
- gerar docx a partir de templates
- revisar estrutura e logica documental
- editar texto complexo
- criar KCS, manuais, relatorios e atas

## Relacoes
- PowerPoint: roteiro de slides pode sair de um documento aprovado
- PDF: docx e fonte editavel; PDF e distribuicao final apos aprovacao

## Fidelidade de arquivos Office e uso controlado do M365

- CSV é apenas formato simples de intercâmbio e staging.
- Quando importam fórmulas, formatação, tabelas, filtros, validações, estilos, layout, múltiplas abas, gráficos, pivots, comentários, proteção ou identidade visual, formatos nativos são preferenciais.
- Formatos principais: .xlsx, .docx, .pptx, .pdf.
- M365/Graph e Office Scripts são HML-gated e não devem conter segredos no Git.
- Office Desktop é fallback interativo e não padrão.
- Adobe Acrobat continua sendo a política padrão para PDF, especialmente para PDF assinado ou sensível.
