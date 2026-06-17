# MACRO-H1C — Runtime Visual Recheck

## Status

`PARTIAL_AUTH_SESSION_REQUIRED`

## Contexto

This boundary rechecked only the authenticated visual flow for the post-movement macro that was fixed in `MACRO-H1` and build-validated in `MACRO-H1B`.

## Ambiente

- Node: Linux Node `~/.nvm/versions/node/v22.22.3/bin/node`
- npm: `10.9.8`
- Build: already validated in `MACRO-H1B`; `frontend/itam-platform/dist` exists
- Runtime: backend `127.0.0.1:8000` responded normally; frontend login page rendered normally

## Estratégia de autenticação

- A tentativa segura usou o navegador local e um perfil temporário separado.
- Não foi exposta nenhuma credencial, cookie, token ou header de autenticação.
- A sessão autenticada do app não estava disponível nesta boundary.

## Cenário validado

- `GET /health` respondeu normalmente.
- `GET /login` respondeu com a tela de login Sentinel.
- O recheck autenticado do fluxo `Ativo -> Movimentação -> Macro -> Copiar` não pôde ser completado sem uma sessão local válida.

## Resultado

- Modal permanece aberta: `não verificado nesta boundary`
- Macro visível: `não verificado nesta boundary`
- Botão copiar: `não verificado nesta boundary`
- Copied endpoint: `não verificado nesta boundary`
- Histórico: `não verificado nesta boundary`
- Auditoria: `não verificado nesta boundary`

## Evidência segura

- URL pública local sem token: `http://127.0.0.1:8000/login`
- Build já validado anteriormente e sem alteração de `package-lock.json`
- Nenhum segredo foi gravado em arquivo versionado

## Bloqueios

- A sessão autenticada do UAT local não ficou disponível de forma segura nesta execução.
- Sem autenticação, o fluxo visual da macro não pode ser repetido com fidelidade.

## Decisão final

`PARTIAL_AUTH_SESSION_REQUIRED`

## Próxima boundary recomendada

`AUTH-UAT-H1 — define safe local UAT authentication path`
