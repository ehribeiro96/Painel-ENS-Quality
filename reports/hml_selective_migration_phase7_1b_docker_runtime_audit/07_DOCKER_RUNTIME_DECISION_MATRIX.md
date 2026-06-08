# Docker Runtime Decision Matrix

| Opção | Vantagem | Risco | Impacto | Decisão |
| --- | --- | --- | --- | --- |
| Manter Docker Desktop WSL por enquanto | menor risco imediato, stack já rodando | dependência do Desktop e licenciamento | baixo agora | recomendado temporariamente |
| Migrar agora para Docker Engine nativo | maior portabilidade futura | risco de perder/duplicar volumes e contexts | alto | rejeitado agora |
| Criar plano de migração sem executar | prepara portabilidade | exige fase adicional | baixo | recomendado |
| Rodar dois daemons em paralelo sem governança | flexível | alto risco de confusão de contextos/volumes | alto | rejeitado |

## Decisão recomendada

`Manter Docker Desktop WSL temporariamente e preparar Fase 7.1C/7.3 de migração Docker Engine nativo sem alterar runtime atual.`
