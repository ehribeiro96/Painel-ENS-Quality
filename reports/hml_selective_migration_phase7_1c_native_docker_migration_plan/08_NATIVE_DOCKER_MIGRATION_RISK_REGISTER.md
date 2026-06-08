# Native Docker Migration Risk Register

| Risco | Severidade | Mitigação |
| --- | ---: | --- |
| Confundir contextos Docker | Alta | usar `docker context show`, `--context`, logs de evidência |
| Perder dados de Postgres | Alta | `pg_dump` + restore validado |
| Perder dados de Qdrant | Alta | snapshot/export validado |
| Redis ter dado persistente não tratado | Média | classificar Redis como cache ou persistente antes |
| Conflito de portas | Média | usar portas alternativas no nativo durante teste |
| Licenciamento Docker Desktop | Média | avaliar política corporativa |
| Copiar volume bruto errado | Alta | evitar volume bruto como estratégia primária |
| Rodar `down -v` por engano | Alta | bloquear comando e exigir aprovação |
| Aplicar context global errado | Alta | preferir `--context` por comando |
