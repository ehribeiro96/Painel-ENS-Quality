# Base44 import staging

Este diretório registra o inventário e as regras do export bruto do frontend Base44 antes e durante a integração visual no Painel ENS-Quality.

Status atual:
- export Base44 localizado em `/home/estevaoqualityadm/base44`
- o source tree foi inventariado
- H1 da importação visual já está sendo aplicado apenas nos pontos seguros do frontend ativo

Regras permanentes:
- manter o export bruto aqui até concluir o inventário
- não usar este staging como fonte de regra de negócio, autenticação ou dados funcionais
- não importar `base44Client.js`, `AuthContext.jsx`, `query-client.js` ou `entities/*.json`
- não substituir rotas reais do Painel ENS-Quality

H1 — importação visual somente:
- shell/layout visual inspirado em Base44
- componentes visuais base (`Base44PageHeader`, `Base44EmptyState`, `Base44StatusBadge`, `Base44Surface`, `Base44MetricCard`, `Base44ShellAccent`)
- login visual
- dashboard visual
- not found visual

O que não foi importado:
- lógica funcional Base44
- mocks Base44
- auth Base44
- API Base44
- entities JSON do export

Checklist futuro:
- Assets e AssetDetail visuais no H2
- manter a revisão de permissões, AI Chat e histórico fora da importação Base44 funcional
