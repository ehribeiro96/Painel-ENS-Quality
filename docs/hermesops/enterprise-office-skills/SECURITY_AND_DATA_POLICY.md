# Security and Data Policy

- nao armazenar senha
- nao armazenar token
- nao armazenar certificado
- nao armazenar PFX/P12
- nao armazenar CPF/RG
- usar sensitivity e external_model_allowed
- documentos reais exigem aprovacao
- PDFs assinados exigem regra especial
- segredos so em HML, nunca no Git

## Fidelidade de arquivos Office e uso controlado do M365

- CSV é apenas formato simples de intercâmbio e staging.
- Quando importam fórmulas, formatação, tabelas, filtros, validações, estilos, layout, múltiplas abas, gráficos, pivots, comentários, proteção ou identidade visual, formatos nativos são preferenciais.
- Formatos principais: .xlsx, .docx, .pptx, .pdf.
- M365/Graph e Office Scripts são HML-gated e não devem conter segredos no Git.
- Office Desktop é fallback interativo e não padrão.
- Adobe Acrobat continua sendo a política padrão para PDF, especialmente para PDF assinado ou sensível.
