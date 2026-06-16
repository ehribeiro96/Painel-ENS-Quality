# B4-E - Legacy CSP and Route Polish

## Resumo executivo

Esta boundary fechou a dependência externa de fontes no legado `/assinaturas/` e `/admin/`, mantendo a CSP restritiva já existente e sem abrir allowlist para Google Fonts.

O ajuste foi deliberadamente pequeno:

- removi o carregamento de `fonts.googleapis.com` e `fonts.gstatic.com` do template legado base;
- troquei o stack tipográfico para fontes locais/sistêmicas;
- mantive o comportamento de CSP por rota já implementado em `backend/app/main.py`;
- gerei evidência visual antes/depois nas rotas legadas.

## Escopo

Permitido nesta boundary:

- `/admin/`
- `/assinaturas/`
- CSP legado
- stack de fontes local/sistêmica
- templates legados de assinatura/administracao

Fora de escopo:

- ImportService
- AI Chat/Ollama
- migrations
- Docker/Compose
- shell React moderno
- package-lock do frontend

## Arquivos alterados

- [assets/templates/base.html](/home/estevaoqualityadm/projects/Painel-ENS-Quality/assets/templates/base.html)
- [assets/static/vendor/tpl/css/templatemo-topic-listing.css](/home/estevaoqualityadm/projects/Painel-ENS-Quality/assets/static/vendor/tpl/css/templatemo-topic-listing.css)
- [docs/audit/README.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/README.md)
- [docs/audit/NEXT_BOUNDARY_DECISION.md](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/NEXT_BOUNDARY_DECISION.md)

## Mudanças funcionais

- O template legado base não referencia mais Google Fonts.
- O tema do legado passou a usar stack local/sistêmica:
  - `system-ui`
  - `-apple-system`
  - `BlinkMacSystemFont`
  - `Segoe UI`
  - `Roboto`
  - `Helvetica`
  - `Arial`
- As variáveis do tema foram alinhadas para não depender de `Open Sans` e `Montserrat`.

## CSP

A lógica de CSP já existente foi preservada:

- CSP estrita para o resto da aplicação;
- CSP legado para `/admin` e `/assinaturas`;
- `Content-Security-Policy-Report-Only` estrito mantido como sinalização de endurecimento futuro.

Validação de cabeçalhos:

- `/assinaturas/` respondeu `200` com CSP legado ativo e sem referência a Google Fonts na captura final.
- `/admin/` respondeu `302` para `/admin/login` e o login legado carregou com CSP legado ativo.

## Evidência visual

Capturas antes:

- [docs/audit/screenshots/b4e-legacy-csp/before/assinaturas.png](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/screenshots/b4e-legacy-csp/before/assinaturas.png)
- [docs/audit/screenshots/b4e-legacy-csp/before/admin-login.png](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/screenshots/b4e-legacy-csp/before/admin-login.png)

Capturas depois:

- [docs/audit/screenshots/b4e-legacy-csp/after/assinaturas.png](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/screenshots/b4e-legacy-csp/after/assinaturas.png)
- [docs/audit/screenshots/b4e-legacy-csp/after/admin-login.png](/home/estevaoqualityadm/projects/Painel-ENS-Quality/docs/audit/screenshots/b4e-legacy-csp/after/admin-login.png)

## Validação

Comandos e verificações executados:

- `curl -I http://127.0.0.1:8000/assinaturas/`
- `curl -I http://127.0.0.1:8000/admin/`
- navegação headless local para screenshots via Chrome do Windows controlado por Node
- varredura de referências para `fonts.googleapis.com`, `fonts.gstatic.com`, `Montserrat` e `Open Sans`

Resultado:

- nenhum request para Google Fonts no estado final;
- nenhuma allowlist nova de fontes externas;
- layout legível mantido nas capturas.

## Riscos restantes

- A rota `/admin/` segue redirecionando para `/admin/login`, o que é esperado.
- O visual do legado permanece dependente do CSS do tema original, agora com stack local.
- Não houve smoke visual interativo nesta sessão, apenas captura headless.

## Decisão final

`GO`
