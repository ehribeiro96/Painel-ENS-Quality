# Prompt de implementação com Codex

## Papel
Prompt de implementação com Codex

## Entrada esperada
Bug ou feature com contexto mínimo necessário, arquivos relevantes, restrições e critérios de aceite.

## Saída esperada
Plano curto, patch sugerido, validação local e riscos.

## Regras de segurança
Enviar somente contexto mínimo. Remover segredos. Não compartilhar dados restricted/[REDACTED_SECRET_KEYWORD].

## Formato
Saída técnica com etapas, diff esperado e testes.

## Critérios de validação
A solução compila/testa localmente ou aponta bloqueio verificável.

## Quando escalar
Escalar se houver código sensível, impacto de produção alto ou dúvida de arquitetura.
