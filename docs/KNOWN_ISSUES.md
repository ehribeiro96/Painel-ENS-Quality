# Known Issues

Status permitidos: `Open`, `In Progress`, `Fixed`, `Won't Fix`, `Deferred`.

## KI-001

ID: KI-001  
Título: UAT visual no navegador ainda depende de execução manual  
Severidade: MEDIUM  
Área: Frontend  
Cenário UAT: UAT-001 a UAT-022  
Descrição: A regressão cobre API, legado, SPA fallback e build, mas os fluxos visuais completos ainda precisam de execução por usuários reais da TI.  
Passos para reproduzir: Executar os cenários em `docs/UAT_SCENARIOS.md`.  
Resultado atual: Validação manual pendente.  
Resultado esperado: Cenários executados, evidências registradas e decisão GO/NO-GO documentada.  
Impacto operacional: Sem execução visual, a aprovação do piloto fica limitada à validação técnica.  
Workaround: Executar o roteiro em `docs/UAT_EXECUTION_SCRIPT.md`.  
Bloqueia UAT? Não.  
Bloqueia release? Bloqueia release amplo sem evidências.  
Responsável: Facilitador UAT / TI.  
Status: Deferred  
Data de abertura: 2026-06-02  
Data de fechamento:

## KI-002

ID: KI-002  
Título: JWT secret deve ser substituído fora do ambiente local  
Severidade: HIGH  
Área: Auth  
Cenário UAT: Segurança operacional  
Descrição: `.env.example` usa placeholder de documentação. Ambientes reais devem definir segredo forte localmente.  
Passos para reproduzir: Revisar variáveis de ambiente antes de subir UAT/piloto.  
Resultado atual: Configuração depende do operador local.  
Resultado esperado: `JWT_SECRET_KEY` forte, único por ambiente e não versionado.  
Impacto operacional: Risco de segurança se default fraco for usado fora de ambiente local controlado.  
Workaround: Definir segredo forte no `.env` local ou secret manager.  
Bloqueia UAT? Não, se UAT for local/controlado.  
Bloqueia release? Sim para produção.  
Responsável: Platform/Release.  
Status: Open  
Data de abertura: 2026-06-02  
Data de fechamento:

## KI-003

ID: KI-003  
Título: Matriz RBAC completa ainda precisa de confirmação por perfis reais  
Severidade: MEDIUM  
Área: Auth  
Cenário UAT: UAT-010  
Descrição: A regressão valida bloqueios essenciais, mas o UAT deve confirmar permissões percebidas por ADMIN, TECHNICIAN, MANAGER e VIEWER.  
Passos para reproduzir: Executar UAT-010 e fluxos por perfil.  
Resultado atual: Cobertura mínima automatizada.  
Resultado esperado: Evidências de leitura/escrita por perfil.  
Impacto operacional: Pode gerar confusão de acesso durante piloto.  
Workaround: Executar cenários por perfil e registrar desvios.  
Bloqueia UAT? Não.  
Bloqueia release? Pode bloquear piloto ampliado se houver permissão insegura.  
Responsável: QA/Produto.  
Status: Deferred  
Data de abertura: 2026-06-02  
Data de fechamento:

## KI-004

ID: KI-004  
Título: Restore deve ser usado apenas em ambiente controlado  
Severidade: HIGH  
Área: Database  
Cenário UAT: UAT-019  
Descrição: O script de restore substitui o banco do project informado.  
Passos para reproduzir: Executar restore em project incorreto.  
Resultado atual: Script exige confirmação ou `-Force` e gera backup pré-restore.  
Resultado esperado: Operador usa apenas `itam_uat`/`itam_validation` nesta fase.  
Impacto operacional: Perda de dados se usado em ambiente errado.  
Workaround: Seguir `docs/BACKUP_RESTORE_RUNBOOK.md` e conferir project name.  
Bloqueia UAT? Não.  
Bloqueia release? Bloqueia uso sem runbook e confirmação operacional.  
Responsável: Release/Platform.  
Status: Open  
Data de abertura: 2026-06-02  
Data de fechamento:

## KI-005

ID: KI-005  
Título: Volume UAT preservado mantém senha admin antiga  
Severidade: MEDIUM  
Área: Auth  
Cenário UAT: Preparação de sessão  
Descrição: Como o bootstrap admin é idempotente, alterar `ADMIN_PASSWORD` depois que o banco já possui o admin não atualiza automaticamente a senha persistida.  
Passos para reproduzir: Subir `itam_uat` com uma senha, parar preservando volumes, subir novamente com outra senha e executar seed.  
Resultado atual: Login do seed falha com credenciais inválidas.  
Resultado esperado: Facilitador usa a senha original do volume ou recria volume de forma explícita após backup.  
Impacto operacional: Pode atrasar preparação do UAT se o operador trocar a senha local entre sessões.  
Workaround: Usar a mesma senha local da primeira criação do volume; para reinício limpo, fazer backup e usar `stop-uat.ps1 -RemoveVolumes` com confirmação explícita.  
Bloqueia UAT? Não, se o facilitador usar a senha correta ou project isolado novo.  
Bloqueia release? Não.  
Responsável: Facilitador UAT / Platform.  
Status: Open  
Data de abertura: 2026-06-02  
Data de fechamento:

## KI-006

ID: KI-006  
Título: Startup do app saía com ExitCode=3 sem traceback quando ADMIN_PASSWORD era curto  
Severidade: CRITICAL  
Área: Backend  
Cenário UAT: Startup UAT  
Descrição: O bootstrap admin aplicava corretamente a política de senha mínima, mas a exceção no lifespan não era registrada com etapa e traceback.  
Passos para reproduzir: Definir `ADMIN_PASSWORD` com menos de 10 caracteres e iniciar o app.  
Resultado atual: Corrigido; `start-uat.ps1` bloqueia senha curta e o backend emite `startup_failed` se a falha ocorrer no startup.  
Resultado esperado: Falha explícita sem impressão de senha.  
Impacto operacional: Antes da correção, impedia UAT e dificultava diagnóstico.  
Workaround: Usar senha local com 10+ caracteres.  
Bloqueia UAT? Não após correção.  
Bloqueia release? Não após correção.  
Responsável: Platform/Backend.  
Status: Fixed  
Data de abertura: 2026-06-02  
Data de fechamento: 2026-06-02

## KI-007

ID: KI-007  
Título: `source_external_key` do Lansweeper ainda não é coluna persistida em assets  
Severidade: MEDIUM  
Área: Importação / Assets  
Cenário UAT: Importação da planilha real Lansweeper  
Descrição: Linhas IP-only ou sem identidade forte agora recebem `source_external_key` no staging/report para revisão, mas o modelo `assets` ainda não possui coluna persistida para reconciliar essa identidade em importações futuras.  
Passos para reproduzir: Normalizar linha Lansweeper com `Name` em formato IP e sem serial/patrimônio/hostname.  
Resultado atual: Linha fica `REVIEW_REQUIRED` com `source_external_key` explicável; não vira hostname falso.  
Resultado esperado futuro: Migration conservadora para persistir origem/chave externa quando a política de reconciliação for aprovada.  
Impacto operacional: Importações futuras de itens IP-only podem exigir revisão manual recorrente.  
Workaround: Completar identidade forte antes do apply ou manter revisão manual para itens IP-only.  
Bloqueia UAT? Não.  
Bloqueia release? Não, desde que conflitos sejam revisados.  
Responsável: Data/Backend.  
Status: Open  
Data de abertura: 2026-06-03  
Data de fechamento:
