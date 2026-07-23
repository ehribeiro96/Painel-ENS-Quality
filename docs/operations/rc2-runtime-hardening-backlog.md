# Backlog pós-hardening de runtime RC2

Itens deliberadamente fora da boundary `APOEMA_V1_0_0_RC2_RUNTIME_HARDENING_P1_REMEDIATION`:

- definir persistência nomeada e plano de migração para o volume atual do Redis;
- remover defaults de credenciais do Compose em boundary própria;
- criar e certificar um ambiente de staging;
- estabelecer backup permanente e executar restore drill controlado;
- revisar separadamente a migration `0007_macro_movement_unique`;
- revisar a mutação preexistente de `model_fields_set` causada pelo default local do AI Chat;
- ampliar a cobertura da proveniência de `ENABLE_AI_CHAT` em boundary própria;
- tratar frontend, Macros, Imports, RBAC e provider Hermes somente em boundaries específicas.

Este backlog não autoriza alteração de dados, migrations, containers ou runtime.
