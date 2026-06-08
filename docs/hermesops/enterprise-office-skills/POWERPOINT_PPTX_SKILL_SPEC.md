# PowerPoint/Pptx Skill Spec

## Casos de uso
- treinamento Service Desk
- treinamento de jovem aprendiz
- apresentacao executiva
- relatorio mensal
- projeto e handoff tecnico

## Operacoes suportadas
- roteiro de slides
- outline
- validacao de narrativa
- validacao de densidade textual
- speaker notes

## Bloqueios
- identidade visual real sem aprovacao
- dados reais sem sanitizacao
- chamada Graph nesta fase

## Fidelidade de arquivos Office e uso controlado do M365

- CSV é apenas formato simples de intercâmbio e staging.
- Quando importam fórmulas, formatação, tabelas, filtros, validações, estilos, layout, múltiplas abas, gráficos, pivots, comentários, proteção ou identidade visual, formatos nativos são preferenciais.
- Formatos principais: .xlsx, .docx, .pptx, .pdf.
- M365/Graph e Office Scripts são HML-gated e não devem conter segredos no Git.
- Office Desktop é fallback interativo e não padrão.
- Adobe Acrobat continua sendo a política padrão para PDF, especialmente para PDF assinado ou sensível.
