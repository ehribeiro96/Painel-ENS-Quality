# Cenários de UAT Operacional

Status inicial: Pendente de execução por usuários reais da TI.

Use estes cenários junto com:

- `docs/UAT_EVIDENCE_TEMPLATE.md`
- `docs/templates/uat_results_template.csv`
- `docs/templates/uat_known_issues_template.csv`

## UAT-001 - Login

Objetivo: Validar acesso autenticado ao sistema.  
Perfil necessário: Administrador TI, Técnico, Viewer ou Gestor.  
Pré-condições: Ambiente UAT ativo; usuário existente.  
Dados necessários: `estevao.quality@ens.edu.br` ou usuário UAT.  
Passos:

1. Abrir `http://127.0.0.1:8080`.
2. Informar e-mail.
3. Informar senha sem expor em print.
4. Confirmar login.
5. Acessar dashboard.

Resultado esperado: Usuário entra no sistema e visualiza dashboard.  
Critério de aceite: Login sem erro e sem exposição de senha.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se login válido falhar; HIGH se houver atrito com workaround.

## UAT-002 - Dashboard

Objetivo: Validar entendimento operacional dos totais.  
Perfil necessário: Administrador TI, Gestor ou Técnico.  
Pré-condições: Massa UAT criada.  
Dados necessários: Ativos `RJMTEST001` a `RJMTEST005`.  
Passos:

1. Abrir dashboard.
2. Verificar ativos em uso.
3. Verificar ativos em estoque.
4. Verificar ativos em manutenção.
5. Verificar ativos defeituosos.
6. Conferir últimas movimentações.

Resultado esperado: Dados fazem sentido para operação.  
Critério de aceite: Cards e listas carregam sem erro e com totais coerentes.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: HIGH se dashboard quebrar; MEDIUM se dado secundário estiver confuso.

## UAT-003 - Criar Usuário

Objetivo: Validar cadastro de colaborador.  
Perfil necessário: Administrador TI.  
Pré-condições: Login admin.  
Dados necessários: `uat.novo.colaborador@ens.edu.br`.  
Passos:

1. Abrir usuários.
2. Criar usuário.
3. Preencher nome, e-mail, departamento e unidade.
4. Salvar.
5. Buscar usuário criado.

Resultado esperado: Usuário criado e listável.  
Critério de aceite: E-mail válido aceito e dados aparecem corretamente.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: HIGH se cadastro falhar; MEDIUM se validação/feedback confundir.

## UAT-004 - Criar Ativo

Objetivo: Validar cadastro manual de ativo.  
Perfil necessário: Técnico ou Administrador TI.  
Pré-condições: Login válido.  
Dados necessários: Hostname `RJMUATMANUAL001`, patrimônio `PAT-UAT-MANUAL-001`, serial `SN-UAT-MANUAL-001`.  
Passos:

1. Abrir ativos.
2. Criar novo ativo.
3. Preencher hostname, patrimônio, serial, tipo, status e localização.
4. Salvar.
5. Abrir detalhe do ativo.

Resultado esperado: Ativo criado e detalhe acessível.  
Critério de aceite: Sem erro 500 e campos principais persistidos.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se criação quebrar fluxo crítico; HIGH se campo essencial não persistir.

## UAT-005 - Buscar Ativo

Objetivo: Validar localização rápida de ativo.  
Perfil necessário: Técnico ou Viewer.  
Pré-condições: Massa UAT criada.  
Dados necessários: `RJMTEST001`, `PAT-UAT-001`, `SN-UAT-001`.  
Passos:

1. Buscar por hostname.
2. Buscar por patrimônio.
3. Buscar por serial.
4. Filtrar por status.
5. Abrir resultado.

Resultado esperado: Ativo correto encontrado em poucos segundos.  
Critério de aceite: Busca/filtros retornam o ativo esperado.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: HIGH se busca principal falhar; MEDIUM se houver lentidão relevante.

## UAT-006 - Detalhe do Ativo

Objetivo: Validar leitura rápida da situação atual.  
Perfil necessário: Técnico ou Viewer.  
Pré-condições: Ativo existente.  
Dados necessários: `RJMTEST001`.  
Passos:

1. Abrir detalhe do ativo.
2. Identificar usuário atual.
3. Identificar status.
4. Identificar localização.
5. Ver histórico/timeline.

Resultado esperado: Situação atual e histórico compreensíveis.  
Critério de aceite: Usuário, status, localização e histórico visíveis.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: HIGH se detalhe não abrir; MEDIUM se histórico estiver confuso.

## UAT-007 - Movimentar Ativo Para Usuário

Objetivo: Validar fluxo crítico estoque -> usuário.  
Perfil necessário: Técnico ou Administrador TI.  
Pré-condições: Ativo em estoque e usuário UAT existente.  
Dados necessários: `RJMTEST003`, usuário `uat.colaborador.teste@ens.edu.br`.  
Passos:

1. Abrir ativo em estoque.
2. Iniciar movimentação.
3. Selecionar novo usuário.
4. Definir status `IN_USE`.
5. Informar localização e justificativa.
6. Conferir before/after.
7. Confirmar.
8. Abrir histórico.

Resultado esperado: Ativo vinculado ao usuário e movimento auditável.  
Critério de aceite: Histórico mostra usuário/status/local anterior e novo.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se movimentação falhar ou não auditar.

## UAT-008 - Enviar Ativo Para Manutenção

Objetivo: Validar movimentação para manutenção.  
Perfil necessário: Técnico.  
Pré-condições: Ativo em uso.  
Dados necessários: Ativo movimentado no UAT-007.  
Passos:

1. Abrir ativo.
2. Iniciar movimentação.
3. Definir status `MAINTENANCE`.
4. Informar local `Laboratório TI`.
5. Informar motivo.
6. Confirmar.
7. Validar histórico.

Resultado esperado: Status manutenção registrado.  
Critério de aceite: Histórico e auditoria refletem mudança.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se histórico/auditoria não registrar; HIGH se feedback falhar.

## UAT-009 - Retornar Ativo ao Estoque

Objetivo: Validar retorno controlado para estoque.  
Perfil necessário: Técnico.  
Pré-condições: Ativo em manutenção.  
Dados necessários: Ativo do UAT-008.  
Passos:

1. Abrir ativo.
2. Movimentar para `STOCK`.
3. Remover usuário, se aplicável.
4. Informar localização `Estoque TI`.
5. Confirmar.
6. Validar detalhe e histórico.

Resultado esperado: Ativo em estoque, sem usuário atual quando aplicável.  
Critério de aceite: Estado atual coerente e histórico preservado.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: HIGH se estado final ficar incoerente.

## UAT-010 - Permissão Viewer

Objetivo: Validar bloqueio de escrita para consulta.  
Perfil necessário: Viewer.  
Pré-condições: Usuário viewer criado.  
Dados necessários: `uat.viewer.teste@ens.edu.br`.  
Passos:

1. Entrar como viewer.
2. Abrir listagem de ativos.
3. Tentar criar ativo.
4. Tentar movimentar ativo.
5. Confirmar que consulta segue disponível.

Resultado esperado: Escrita bloqueada com 403 ou UI sem ação, leitura permitida.  
Critério de aceite: Viewer não altera dados.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se viewer escrever; HIGH se erro for 500.

## UAT-011 - Auditoria

Objetivo: Validar rastreabilidade operacional.  
Perfil necessário: Administrador TI.  
Pré-condições: Movimentação executada.  
Dados necessários: Movimento do UAT-007/008/009.  
Passos:

1. Abrir auditoria.
2. Buscar evento de movimentação.
3. Conferir usuário responsável.
4. Conferir before/after.
5. Conferir timestamp.

Resultado esperado: Evento localizável e compreensível.  
Critério de aceite: Log contém entidade, ação, usuário e snapshots quando disponíveis.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se auditoria crítica não existir.

## UAT-012 - Importação Lansweeper Válida

Objetivo: Validar ingestão pequena válida.  
Perfil necessário: Técnico ou Administrador TI.  
Pré-condições: Ambiente UAT ativo.  
Dados necessários: `tests/fixtures/uat/lansweeper_valid_uat.csv`.  
Passos:

1. Abrir importações.
2. Upload do CSV válido.
3. Revisar status.
4. Revisar staging/relatório.

Resultado esperado: Registros válidos classificados sem corromper inventário.  
Critério de aceite: Totais coerentes e sem erro inesperado.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: HIGH se importação válida falhar.

## UAT-013 - Importação Com Duplicidade

Objetivo: Validar detecção de duplicidade.  
Perfil necessário: Técnico ou Administrador TI.  
Pré-condições: CSV válido já importado ou ativos equivalentes existentes.  
Dados necessários: `tests/fixtures/uat/lansweeper_duplicate_uat.csv`.  
Passos:

1. Upload do CSV duplicado.
2. Revisar conflitos.
3. Validar que inventário não foi sobrescrito indevidamente.

Resultado esperado: Duplicidade identificada e reportada.  
Critério de aceite: Conflitos visíveis e inventário íntegro.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se duplicidade corromper inventário.

## UAT-014 - Importação Inválida/Maliciosa

Objetivo: Validar bloqueio de entrada insegura/inválida.  
Perfil necessário: Técnico ou Administrador TI.  
Pré-condições: Ambiente UAT ativo.  
Dados necessários: `lansweeper_invalid_uat.csv` e `lansweeper_formula_injection_uat.csv`.  
Passos:

1. Upload do CSV inválido.
2. Conferir erros de validação.
3. Upload do CSV com fórmula.
4. Conferir bloqueio/sanitização.

Resultado esperado: Erros reportados e inventário preservado.  
Critério de aceite: Dados maliciosos não são aplicados cegamente.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se payload malicioso for aplicado de forma insegura.

## UAT-015 - Assinatura Corporativa Nova

Objetivo: Validar geração de assinatura.  
Perfil necessário: Técnico ou Administrador TI.  
Pré-condições: Usuário com dados corporativos.  
Dados necessários: Usuário UAT.  
Passos:

1. Abrir assinaturas.
2. Selecionar usuário.
3. Gerar assinatura.
4. Visualizar HTML.
5. Baixar/copiar, se disponível.

Resultado esperado: HTML contém dados corretos e layout utilizável.  
Critério de aceite: Nome/e-mail/cargo/departamento aparecem quando preenchidos.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: HIGH se assinatura não renderizar.

## UAT-016 - Legado `/assinaturas/`

Objetivo: Validar preservação do legado.  
Perfil necessário: Técnico ou Administrador TI.  
Pré-condições: Ambiente UAT ativo.  
Dados necessários: Nenhum dado real.  
Passos:

1. Acessar `/assinaturas/`.
2. Validar carregamento.
3. Validar assets básicos.

Resultado esperado: Página responde 200 e comportamento legado preservado.  
Critério de aceite: Sem 404/500.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se legado quebrar.

## UAT-017 - Legado `/admin/`

Objetivo: Validar admin legado.  
Perfil necessário: Administrador TI.  
Pré-condições: Ambiente UAT ativo.  
Dados necessários: Nenhum dado real.  
Passos:

1. Acessar `/admin/`.
2. Validar comportamento esperado.
3. Registrar se retorna 200 ou 302.

Resultado esperado: 200 ou 302 esperado, sem erro crítico.  
Critério de aceite: Admin legado segue montado.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: HIGH se `/admin/` quebrar sem workaround.

## UAT-018 - Backup Durante UAT

Objetivo: Validar backup operacional durante sessão.  
Perfil necessário: Facilitador.  
Pré-condições: Ambiente UAT ativo.  
Dados necessários: Massa UAT.  
Passos:

1. Rodar `.\scripts\ops\backup-db.ps1 -ProjectName itam_uat`.
2. Conferir `.dump`.
3. Conferir manifesto.
4. Conferir SHA256 e tamanho.

Resultado esperado: Backup criado sem imprimir senha.  
Critério de aceite: Arquivo e manifesto existem.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se backup falhar.

## UAT-019 - Restore Controlado

Objetivo: Validar restauração segura.  
Perfil necessário: Facilitador.  
Pré-condições: Backup disponível e autorização da sessão.  
Dados necessários: Backup UAT.  
Passos:

1. Confirmar que é ambiente `itam_uat`.
2. Rodar restore controlado.
3. Validar smoke pós-restore.
4. Validar login/listagem.

Resultado esperado: Banco restaurado e app saudável.  
Critério de aceite: Health e smokes passam após restore.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: BLOCKER se restore destruir ambiente sem recuperação; CRITICAL se falhar.

## UAT-020 - Logout e Sessão Expirada

Objetivo: Validar encerramento de sessão.  
Perfil necessário: Todos.  
Pré-condições: Login ativo.  
Dados necessários: Usuário UAT.  
Passos:

1. Fazer logout.
2. Tentar acessar rota protegida.
3. Validar exigência de login.

Resultado esperado: Sessão encerrada e acesso protegido bloqueado.  
Critério de aceite: Sem acesso indevido após logout.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: CRITICAL se sessão permanecer válida indevidamente.

## UAT-021 - Refresh de Página em Deep Link

Objetivo: Validar fallback SPA.  
Perfil necessário: Todos.  
Pré-condições: Ambiente UAT ativo.  
Dados necessários: URL `/assets`, `/users`, `/imports`.  
Passos:

1. Abrir `/assets`.
2. Atualizar página.
3. Repetir em `/users` e `/imports`.

Resultado esperado: SPA carrega sem 404 indevido.  
Critério de aceite: Deep links carregam corretamente.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: HIGH se refresh quebrar navegação principal.

## UAT-022 - Busca/Filtro Com Múltiplos Status

Objetivo: Validar filtro operacional combinado.  
Perfil necessário: Técnico ou Viewer.  
Pré-condições: Massa com múltiplos status.  
Dados necessários: Ativos em `IN_USE`, `STOCK`, `MAINTENANCE`, `DEFECTIVE`.  
Passos:

1. Abrir ativos.
2. Filtrar por status em uso.
3. Filtrar por estoque.
4. Filtrar por manutenção.
5. Combinar busca textual com filtro.
6. Limpar filtros.

Resultado esperado: Filtros respondem coerentemente e podem ser limpos.  
Critério de aceite: Resultado visível corresponde ao filtro aplicado.  
Status: Pendente.  
Observação:  
Evidência:  
Critério de severidade: MEDIUM se filtro secundário falhar; HIGH se busca principal falhar.

