# security_rules.md

Procedural memory rule set with human review requirement.

## Escopo
- Block secrets, tokens and certificates.
- Restricted content stays local.
- Audit every memory promotion.

## Validação
- Offline only
- Dados sintéticos
- Revisão humana quando aplicável

## Riscos
- Memória ou classificação incorreta se a fonte for fraca
- Conflitos precisam revisão humana

## Rollback
- Remover candidatos inválidos e registrar motivo

## pt-BR
- pt-BR é o idioma padrão de resposta operacional do HermesOps, salvo quando o usuário pedir outro idioma ou quando a sintaxe técnica exigir preservação em inglês.
- Informações sensíveis jamais devem ser abertas ou copiadas.
- Quando houver risco, registrar a evidência e fazer rollback seguro.
