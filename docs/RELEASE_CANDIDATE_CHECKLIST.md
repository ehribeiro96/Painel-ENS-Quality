# Release Candidate Interno - Checklist

Data base: 2026-06-02  
Escopo: UAT controlado da plataforma ITAM enterprise com legado de assinaturas preservado.

## Decisão

Status: GO COM RESSALVAS

Ressalvas: UAT visual ainda precisa ser executado por usuários reais. Nenhuma ressalva atual exige feature nova.

## Checklist

| Item | Critério | Como validar | Resultado esperado | Status | Evidência | Observação |
|---|---|---|---|---|---|---|
| Arquitetura | Monólito modular preservado | Revisar `backend/app` e docs | Domínios separados e legado montado | Passou | Revisões arquiteturais anteriores | Não refatorar nesta fase |
| Backend | FastAPI importa e compila | `python -m compileall -q backend/app backend/alembic tests` | Sem erro | Passou | Executado em 2026-06-02 |  |
| Frontend | Vite builda | `npm run build` em `frontend/itam-platform` | Build concluído | Passou | Vite build gerado |  |
| Banco | PostgreSQL sobe no Compose | `scripts/ops/start-uat.ps1` | Postgres healthy | Passou | Project `itam_uat` |  |
| Migrations | Alembic aplica no startup | Logs/startup e `alembic current` | Current no head | Validado anteriormente | Relatório operacional | Revalidar no UAT |
| Docker | Configuração válida | `docker compose config --services` | `postgres`, `redis`, `app` | Passou | Serviços listados |  |
| Auth | Login, refresh e logout reais | Suíte de regressão | Tokens válidos e logout efetivo | Validado anteriormente | Suíte operacional | Senha via env local |
| RBAC | VIEWER não escreve | Teste protegido | 403, não 500 | Validado anteriormente | Regressão |  |
| Usuários | CRUD básico | API e UAT-003 | Criar/listar/editar | Validado anteriormente | Regressão |  |
| Ativos | CRUD e filtros básicos | API e UAT-004/005 | Criar/listar/buscar | Validado anteriormente | Regressão |  |
| Movimentações | Histórico imutável | UAT-007/008/009 | Before/after e responsável | Validado anteriormente | Regressão |  |
| Histórico | Timeline consultável | `GET /assets/{id}/history` | Eventos ordenados | Validado anteriormente | Regressão |  |
| Auditoria | Ações críticas registradas | `GET /api/v1/audit-logs` | Logs com contexto | Validado anteriormente | Regressão |  |
| Importação | CSV válido/duplicado/inválido | UAT-011/012/013 | Staging e conflitos | Validado anteriormente | Regressão |  |
| Dashboard | Dados operacionais reais | Endpoints dashboard | Totais coerentes | Validado anteriormente | Regressão |  |
| Assinaturas API | HTML de assinatura | UAT-014 | HTML renderizado | Validado anteriormente | Regressão |  |
| `/assinaturas/` | Legado responde | Smoke HTTP | 200 | Validado anteriormente | Regressão |  |
| `/admin/` | Legado preservado | Smoke HTTP | 200 ou 302 esperado | Validado anteriormente | Regressão |  |
| Suíte regressão | Contratos críticos protegidos | `python -m unittest discover -s tests` com UAT ativo | 21 testes OK | Passou | Project `itam_uat` | Teste de migration agora aceita project via env |
| Backup | Dump custom válido | `scripts/ops/backup-db.ps1 -ProjectName itam_uat` | `.dump` e manifesto | Passou | `backups/itam_backup_20260602_080908.dump` | SHA256 no manifesto |
| Restore | Restore controlado | `scripts/ops/restore-db.ps1 -ProjectName itam_uat ... -Force` | Health pós-restore | Passou | Smoke pós-restore 200/302/401 | Backup pré-restore criado |
| Documentação | UAT pronto para TI | Docs desta fase | Plano e cenários claros | Passou | Este pacote |  |
| Riscos conhecidos | Registrados | `docs/KNOWN_ISSUES.md` | Sem blocker aberto | Passou | Este pacote |  |

## Critérios GO

- Stack UAT sobe com `scripts/ops/start-uat.ps1`.
- Smoke passa: `/health`, `/`, `/assinaturas/`, `/admin/`, `/api/v1/assets` sem token retorna 401.
- Backup gera `.dump` com SHA256 e manifesto.
- Restore executa em ambiente controlado e health passa depois.
- Regressão backend e build frontend passam.
- Nenhuma senha real aparece em arquivos versionados.

## Resultado do UAT Operacional

UAT executado? Pendente de execução por usuários reais.  
Data do UAT:  
Participantes:  
Total de cenários: 22  
Aprovados:  
Aprovados com ressalva:  
Reprovados:  
BLOCKER:  
CRITICAL:  
HIGH:  
MEDIUM:  
LOW:  
Backup inicial:  
Backup final:  
Restore testado?  
Decisão: GO COM RESSALVAS até fechamento do UAT visual.

Opções de decisão:

- GO
- GO COM RESSALVAS
- NO-GO
