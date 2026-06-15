# CSP Hardening Report

## Objetivo

Endurecer a CSP sem quebrar a SPA, o preview de assinatura, o legado em `/admin/` e `/assinaturas/`, ou o fluxo de `ai-chat`.

## Política aplicada

- SPA e rotas modernas: `script-src 'self'`.
- `style-src` continua permitindo `'unsafe-inline'` por causa de atributos inline gerados pelo frontend React/Vite atual.
- Legado `/admin/` e `/assinaturas/`: mantém compatibilidade com `unsafe-inline` em `script-src` e `style-src`.
- Legado recebe também `Content-Security-Policy-Report-Only` com política estrita para fase de observação.

## Motivação

- Remover `unsafe-inline` de `script-src` é seguro nesta rodada para a SPA.
- Remover `unsafe-inline` de `style-src` ainda tem risco por uso de estilos inline no frontend e pelo legado WSGI.
- A fase observada evita quebrar `/admin/` e `/assinaturas/` enquanto expõe o risco restante.

## Cabeçalhos validados

- `content-security-policy`
- `content-security-policy-report-only` nas rotas legadas
- `x-content-type-options`
- `x-frame-options`
- `referrer-policy`
- `permissions-policy`

## Validação

- `tests/test_security_headers.py`

## Risco residual

- `style-src` ainda depende de `'unsafe-inline'` na SPA e no legado.
- O próximo passo seguro seria eliminar esses estilos inline gradualmente com medição de impacto.
