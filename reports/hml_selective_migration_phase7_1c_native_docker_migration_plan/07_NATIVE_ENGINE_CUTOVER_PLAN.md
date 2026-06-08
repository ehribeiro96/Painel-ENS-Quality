# Plano Futuro de Cutover - Docker Desktop para Docker Engine Nativo

## Status

Plano documental. Cutover não executado.

## Estratégia recomendada

1. Manter runtime atual rodando no Docker Desktop até backup lógico ser validado.
2. Criar Docker Engine nativo em fase separada.
3. Validar context nativo sem trocar default global.
4. Subir stack em daemon nativo somente em janela controlada.
5. Usar portas alternativas se o stack antigo continuar rodando.
6. Restaurar dados no daemon nativo.
7. Executar probes.
8. Comparar resultados.
9. Só então decidir parada do stack antigo.

## Cutover seguro

- Preferir blue/green temporário com portas alternativas.
- Não disputar as mesmas portas entre daemons.
- Não apagar volumes do Docker Desktop até validação completa no nativo.

## Critério de sucesso

- PostgreSQL restore OK.
- Redis política definida.
- Qdrant restore/snapshot OK.
- Compose config OK.
- Containers running.
- Probes OK.
- Sem secrets em logs.
- Sem Composio executado.

## Critério de rollback

- Manter stack antigo intacto.
- Se nativo falhar, parar apenas stack nativo.
- Não remover dados antigos.
