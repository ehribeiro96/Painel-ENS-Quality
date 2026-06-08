# Checklist Rápido do Facilitador UAT

## Antes do UAT

- [ ] Docker Desktop ativo.
- [ ] Docker Compose disponível.
- [ ] `ADMIN_EMAIL` configurado.
- [ ] `ADMIN_PASSWORD` configurado localmente e não documentado.
- [ ] `ADMIN_NAME` configurado.
- [ ] Ambiente UAT parado antes de iniciar.
- [ ] Se volumes UAT forem preservados, usar a mesma senha admin da primeira criação do banco.
- [ ] Backups antigos identificados.
- [ ] Porta `8080` livre.
- [ ] Documentos de UAT abertos.
- [ ] Participantes e perfis definidos.
- [ ] Massa de teste preparada.
- [ ] CSVs de teste prontos em `tests/fixtures/uat`.
- [ ] Pasta de evidências pronta.
- [ ] Senha não aparece em prints, docs ou logs.

## Durante o UAT

- [ ] Registrar horário de início.
- [ ] Registrar participantes.
- [ ] Executar cenários em ordem.
- [ ] Capturar prints sem senha/token/cookie.
- [ ] Registrar erros no CSV.
- [ ] Classificar severidade.
- [ ] Não corrigir itens não bloqueantes durante a sessão.
- [ ] Atualizar known issues quando necessário.
- [ ] Pausar se houver BLOCKER ou CRITICAL.

## Depois do UAT

- [ ] Gerar backup final.
- [ ] Rodar smoke final.
- [ ] Rodar regressão, salvo justificativa.
- [ ] Gerar relatório.
- [ ] Decidir GO/GO COM RESSALVAS/NO-GO.
- [ ] Parar ambiente.
- [ ] Preservar volumes, salvo decisão explícita.
- [ ] Documentar próximos passos.
