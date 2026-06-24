# AI Chat Parity Matrix — 2026-06-23

| Capacidade | /ai-chat legacy | Apoema Chat | Paridade | Observação |
|---|---|---|---|---|
| Rota protegida | sim | sim | sim | ambas passam por `ProtectedRoute` |
| Composer | sim | sim | sim | ambos têm área de composição ativa |
| Mensagens | sim | sim | sim | ambos renderizam fluxo de mensagens |
| Provider/model selector | sim | sim | sim | Apoema expõe catálogo e modelo |
| Anexos | sim | sim | sim | Apoema aceita anexos locais com metadados |
| Warning de anexos sensíveis | sim | sim | sim | ambos sinalizam arquivos sensíveis |
| Fallback offline | sim | sim | sim | fallback só ocorre em rede/offline real |
| 401/403 sem mock | sim | sim | sim | erros de auth/permissão seguem como falha real |
| Retry/regenerate | sim | parcial | parcial | Apoema tem retry de catálogo; regeneração de mensagem segue como trabalho futuro |
| Copiar resposta | sim | parcial | parcial | legado copia mensagens; Apoema ainda pode evoluir nessa ação |
| Estado vazio | sim | parcial | parcial | legacy mostra painel vazio; Apoema usa mensagens iniciais locais |
| Loading/error | sim | sim | sim | banners e estados explícitos existem nos dois fluxos |
| PT-BR | sim | sim | sim | copy e estados estão em português |
| Responsividade | sim | sim | sim | ambos mantêm layout responsivo |

## Política escolhida
POLICY_A_SAFE_REDIRECT

## Critério mínimo atendido
- ProtectedRoute preservado
- composer existe
- mensagens existem
- erro de backend controlado
- 401/403 não caem em mock
- fallback só em rede/offline
- rota Apoema Chat existe e pode receber o alias legado
- build/test passam

parity_minimum_met: true

## Conclusão
`/ai-chat` pode ser tratado como alias de compatibilidade para `/apoema/chat` sem apagar o módulo legado em disco.
