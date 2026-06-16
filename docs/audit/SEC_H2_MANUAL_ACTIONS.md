# SEC-H2 — Manual Actions Plan

Este plano não foi executado. Ele descreve ações manuais seguras para o humano executar fora desta boundary.

## Para `123` e `123.pub`

1. Revisar fora do Hermes, sem colar o conteúdo no chat.
2. Se forem chaves SSH:
   - mover para `~/.ssh/` ou outro local seguro fora do repositório;
   - aplicar permissões adequadas (`600` para chave privada, `644` para `.pub`, conforme política local);
   - registrar no Git apenas que foram removidas do worktree, nunca o conteúdo;
   - se já foram usadas em algum serviço, considerar rotação.
3. Se forem arquivos descartáveis:
   - remover manualmente somente após confirmação humana;
   - não usar `git clean` para isso.
4. Se não forem chaves/segredos:
   - renomear/mover fora do repo ou justificar explicitamente antes de qualquer commit.

## Para `imports/`

1. Manter fora do Git.
2. Mover dados reais para storage seguro fora do repositório, se forem necessários.
3. Se houver material útil para teste:
   - criar fixture anonimizada em boundary própria;
   - garantir que não contenha dados reais, identificadores internos, nomes pessoais ou evidências operacionais.
4. Não abrir conteúdo no chat e não anexar arquivos.

## Para screenshots operacionais

1. Não usar OCR.
2. Revisar visualmente fora do Hermes se há dados pessoais/operacionais.
3. Se forem necessárias como evidência, redigir ou recriar com dados fictícios.
4. Se forem locais, decidir ignore em `IGNORE-H2`.

## Para `_migration_proposals/`, `_audit_findings/` e `ai-lab/`

1. Separar documentação útil de outputs locais.
2. Não commitar árvore inteira.
3. Revisar paths com termos `token`, `secret`, `credential`, `password`, `database`, `cert`.
4. Promover apenas documentação sanitizada para `docs/` se necessário.

## Para arquivos sensíveis no histórico

Nesta boundary não foi detectado histórico para `123`, `123.pub` ou `imports/`.

Se em boundary futura algum item sensível aparecer tracked ou no histórico:

1. Parar a boundary funcional.
2. Abrir `SEC-H3 — git history sensitive artifact remediation plan`.
3. Não reescrever histórico sem aprovação explícita.
4. Avaliar rotação do segredo antes de qualquer limpeza Git.
