# 02 Filemode Normalization Plan

## Estado observado
- `core.filemode=true`
- `git diff --summary` não mostrou alterações mode-only no tracked tree atual.
- `git diff --numstat` também não trouxe alterações relevantes.

## Plano
- Não há normalização de bits de execução a aplicar agora no baseline rastreado.
- Se arquivos importados ou copiados vierem com bits errados, a correção deve acontecer em commit separado.
- Arquivos de texto e configuração devem permanecer com modo padrão `100644`.
- Scripts executáveis só devem ter `100755` quando forem invocados diretamente.

## Conclusão
- Não existe uma fila ativa de mode changes para corrigir no Git versionado atual.
- O risco real está no volume de arquivos untracked e em artefatos gerados fora do baseline.

