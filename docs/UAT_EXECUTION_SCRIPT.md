# Roteiro Executável de UAT Operacional

## 1. Objetivo

Validar com usuários reais da TI se a plataforma interna de Gestão de Ativos de TI e Assinaturas Corporativas está pronta para piloto controlado, com foco em operação diária, rastreabilidade, segurança, backup/restore e preservação do legado.

## 2. Escopo

- Login, refresh/logout e sessão.
- Dashboard operacional.
- Usuários, ativos, busca, filtros, detalhe, movimentação, histórico e auditoria.
- Importação Lansweeper por CSV pequeno.
- Assinaturas corporativas pela API e legado `/assinaturas/`.
- Admin legado `/admin/`.
- Backup inicial, backup final e restore controlado.

## 3. Fora de Escopo

- IA, Azure AD, Microsoft Graph e Lansweeper API.
- Novas telas, novos módulos ou mudança de arquitetura.
- Dados reais sensíveis.
- Restore em produção.

## 4. Papéis

- Facilitador: conduz a sessão, executa scripts e consolida evidências.
- Administrador TI: valida cadastros, auditoria, permissões e importação.
- Técnico de TI: valida busca, ativos, movimentações e histórico.
- Viewer/Consulta: valida leitura e bloqueio de escrita.
- Gestor: valida dashboard e leitura operacional, se disponível.

## 5. Regras da Sessão

- Não registrar senha em documento, print, log ou chat.
- Usar apenas massa `TEST`/`UAT`.
- Não corrigir itens não bloqueantes durante a sessão.
- BLOCKER ou CRITICAL podem pausar o UAT para diagnóstico.
- HIGH, MEDIUM e LOW devem ser registrados em `KNOWN_ISSUES.md` ou CSV de issues.

## 6. Severidade

- BLOCKER: impede continuação do UAT ou compromete dados/segurança.
- CRITICAL: quebra fluxo crítico como login, movimentação, auditoria, backup ou permissões.
- HIGH: prejudica operação diária, mas há workaround controlado.
- MEDIUM: atrito relevante ou inconsistência sem bloquear fluxo.
- LOW: ajuste cosmético, texto ou melhoria menor.

## 7. Preparação

```powershell
$env:ADMIN_EMAIL="estevao.quality@ens.edu.br"
$env:ADMIN_PASSWORD="<DEFINIR_LOCALMENTE_NAO_COMMITAR>"
$env:ADMIN_NAME="Estevão Ribeiro"
.\scripts\ops\prepare-uat-session.ps1
```

Anotar o caminho da pasta `uat_evidence/YYYYMMDD_HHMMSS/` gerada.

## 8. Abertura Oficial

1. Registrar horário de início.
2. Confirmar participantes e perfis.
3. Confirmar que senha não será registrada.
4. Confirmar URL: `http://127.0.0.1:8080`.
5. Confirmar backup inicial.
6. Abrir `docs/UAT_SCENARIOS.md`.
7. Abrir `docs/templates/uat_results_template.csv`.

## 9. Cenários

Executar `UAT-001` a `UAT-022` em ordem. Para cada cenário:

1. Ler objetivo e pré-condições.
2. Executar passos numerados.
3. Capturar evidência sem senha/token/cookie.
4. Registrar resultado no CSV.
5. Registrar issue quando necessário.

## 10. Evidências

Usar `docs/UAT_EVIDENCE_TEMPLATE.md` como padrão. Salvar prints e arquivos fora do repositório ou na pasta `uat_evidence/`, que deve permanecer ignorada.

## 11. Bugs

Registrar no CSV `uat_known_issues_template.csv` e, quando relevante, consolidar em `docs/KNOWN_ISSUES.md`.

## 12. Critérios de Decisão

NO-GO:

- BLOCKER aberto.
- CRITICAL aberto.
- Login, movimentação, auditoria, backup/restore ou RBAC inseguro falha.

GO COM RESSALVAS:

- Sem BLOCKER/CRITICAL.
- Existem HIGH/MEDIUM documentados com workaround.

GO:

- Sem BLOCKER/CRITICAL/HIGH abertos.
- Fluxos críticos aprovados.

## 13. Encerramento

```powershell
.\scripts\ops\finish-uat-session.ps1 -SessionDir "<CAMINHO_DA_SESSAO>"
```

Gerar relatório:

```powershell
.\scripts\ops\generate-uat-report.ps1 `
  -ResultsCsv "<CAMINHO_DO_CSV_RESULTADOS>" `
  -KnownIssuesCsv "<CAMINHO_DO_CSV_ISSUES>" `
  -SessionDir "<CAMINHO_DA_SESSAO>"
```

Parar ambiente sem remover volumes:

```powershell
.\scripts\ops\stop-uat.ps1 -StopOnly
```

## 14. Checklist Final

- [ ] Participantes registrados.
- [ ] Todos os cenários executados ou justificados.
- [ ] Evidências salvas.
- [ ] Bugs classificados.
- [ ] Backup final gerado.
- [ ] Regressão pós-UAT executada ou justificativa registrada.
- [ ] Relatório UAT gerado.
- [ ] Decisão GO/GO COM RESSALVAS/NO-GO registrada.

