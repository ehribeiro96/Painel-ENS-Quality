# Relatorio de Extracao do Motor de Assinatura

Data: 2026-06-02

## Fontes analisadas

Projeto atual:

- `src/legacy/flask_app.py`
- `src/legacy/signature_model_spec.py`
- `src/legacy/assets_base64.py`
- `assets/templates/`
- `assets/static/`
- `backend/app/domains/signatures/service.py`
- `backend/app/api/v1/routes/signatures.py`

Pasta externa:

- `C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\src\legacy\flask_app.py`
- `C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\src\legacy\signature_model_spec.py`
- `C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\src\legacy\assets_base64.py`
- `C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\assets\templates\`
- `C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\assets\static\`

Itens sensiveis ou bancos foram apenas classificados, nao copiados.

## Funcoes uteis encontradas

| Funcao | Utilidade | Decisao |
|---|---|---|
| `assinatura_html_precisa` | HTML canonico para Outlook classico | Usar como referencia de layout. |
| `assinatura_html_outlook_new` | HTML para Novo Outlook/Web | Usar como referencia de compatibilidade. |
| `_resolver_contexto_assinatura` | Normalizacao de nome, cargo, telefone e endereco | Recriar de forma simples sobre `User` PostgreSQL. |
| `linha_icones_html` | Renderizacao de icones sociais | Reaproveitar conceito usando assets existentes. |
| `gerar_documento_word_assinatura` | Gera DOCX com `python-docx` | Manter fora do fluxo novo ate validacao dedicada. |
| `_assert_html_assinatura_canonica` | Verifica marcadores do HTML legado | Manter como referencia de testes futuros. |

## Templates e assets uteis

- `assets/static/icons/Logo.png`
- `assets/static/icons/linkedin.png`
- `assets/static/icons/instagram.png`
- `assets/static/icons/youtube.png`
- `assets/templates/hero_outlook.html`
- `assets/static/v4/hero-outlook.css`
- `assets/static/v4/hero-outlook.js`
- `assets/static/ASSINATURAS DE E-MAIL (...).docx`

## Partes dependentes de SQLite

- consultas em `src/legacy/flask_app.py`;
- bootstrap e schema de `ens.db`;
- admin Flask;
- busca publica por colaborador legado;
- rotas de edicao/exclusao/ativacao legadas.

Essas partes nao entram no fluxo novo.

## Partes dependentes de AD/Graph/SMTP

- MSAL/Graph em `src/legacy/flask_app.py`;
- envio de assinatura por Graph;
- fallback SMTP;
- `.env` e `secrets`.

Nao foram portadas nesta etapa.

## Implementacao aplicada

O novo `SignatureService` foi atualizado para renderizar HTML corporativo em
tabelas, com CSS inline, logo/icones locais e aviso bilingue. Ele recebe apenas
`User` do PostgreSQL e nao importa Flask, SQLite, SMTP ou Graph.

Arquivos alterados:

- `backend/app/domains/signatures/service.py`
- `tests/test_signatures_postgres_flow.py`

## O que ficou no fallback

- `/assinaturas/`
- `/admin/`
- fluxo publico legado baseado em SQLite;
- DOCX legado;
- Graph/SMTP legado.

## Plano tecnico futuro

1. Criar `renderer.py` separado se o servico crescer.
2. Adicionar teste de fidelidade visual contra marcadores canonicos.
3. Avaliar migration conservadora para campos adicionais de colaborador.
4. Habilitar DOCX apenas se o modelo legado e `python-docx` forem validados.
5. Remover dependencia operacional do fallback somente apos UAT e migração de
   dados de colaboradores para PostgreSQL.
