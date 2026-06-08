# PDF/Adobe Acrobat Skill Spec

## Contexto corporativo
O padrao da empresa para PDF e Adobe Acrobat.

## Casos de uso
- revisao de PDF
- OCR
- combinacao e divisao
- validacao de assinatura digital
- redaction e sanitizacao

## Bloqueios
- abrir PDF real sensivel
- alterar PDF assinado
- manipular certificado
- chamar Adobe API nesta fase

## Fidelidade de arquivos Office e uso controlado do M365

- CSV é apenas formato simples de intercâmbio e staging.
- Quando importam fórmulas, formatação, tabelas, filtros, validações, estilos, layout, múltiplas abas, gráficos, pivots, comentários, proteção ou identidade visual, formatos nativos são preferenciais.
- Formatos principais: .xlsx, .docx, .pptx, .pdf.
- M365/Graph e Office Scripts são HML-gated e não devem conter segredos no Git.
- Office Desktop é fallback interativo e não padrão.
- Adobe Acrobat continua sendo a política padrão para PDF, especialmente para PDF assinado ou sensível.
