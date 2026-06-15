# AI Chat Rate Limit Redis Report

## Objetivo

Migrar o rate limit do `ai-chat` de memória por processo para um store compartilhado com Redis em ambientes multi-worker ou multi-container, preservando fallback local controlado.

## Implementação

- Store abstrato: `RateLimitStore`.
- Store local: `MemoryRateLimitStore`.
- Store compartilhado: `RedisRateLimitStore`.
- Chave: `ai_chat:rate_limit:{user_id_hash}:{window_epoch}`.
- TTL: 60 segundos.
- Limite: continua usando `AI_CHAT_RATE_LIMIT_PER_MINUTE`.
- Resposta de limite: `429 ai_chat_rate_limit_exceeded`.

## Política de ambiente

- `local`: usa memória por padrão, com fallback controlado.
- `staging` e `production`: usam Redis como store principal.
- Falha de Redis fora de `local`: retorna `503 ai_chat_rate_limit_unavailable` e registra o problema sem expor `user_id`, prompt ou chave.

## Segurança

- `user_id` cru não é logado.
- Prompt completo não é registrado no metadata de rate limit.
- API key não é logada pelo fluxo de rate limit.

## Validação

- `tests/test_ai_chat_rate_limit.py`
- `tests/test_ai_chat_hardening.py`

Cobertura validada:

- store em memória expira a janela;
- store Redis fake funciona;
- limite retorna `429`;
- abaixo do limite retorna sucesso;
- rate limit é por usuário;
- fallback local permanece funcional.
