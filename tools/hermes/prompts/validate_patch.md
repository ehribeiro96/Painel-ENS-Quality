# Validar patch

Revise as alteracoes locais e valide se o patch esta pronto.

Verifique:
- Regressao funcional.
- Violacao das regras do projeto.
- Falta de auditoria em alteracoes persistentes.
- DTOs ausentes quando model SQLAlchemy nao deveria ser retornado diretamente.
- Estados de loading, erro e sucesso quando houver UI.
- Comandos de validacao necessarios.

Retorne achados por severidade e inclua o proximo comando recomendado.
