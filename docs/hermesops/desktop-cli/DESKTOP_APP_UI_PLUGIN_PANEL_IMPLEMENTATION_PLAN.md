# DESKTOP_APP_UI_PLUGIN_PANEL_IMPLEMENTATION_PLAN

## Objetivo futuro
Adicionar um painel visual no Hermes Desktop App:

```text
Plugins
└── Composio
    Status: disabled
    Ambiente: test
    Modo: dry-run
    Rede: bloqueada
    Credenciais: não configuradas
    Ações externas: bloqueadas
    Logs: habilitados localmente
    Change proposals: propostas somente
    HML obrigatório: sim
```

## Pré-condições
1. localizar o repositório/source real do Desktop App;
2. criar branch separada;
3. rodar `npm`/`pnpm`/`yarn` somente após autorização;
4. auditar `package.json`;
5. identificar o framework visual;
6. localizar componentes de navegação;
7. localizar integração com o backend Hermes;
8. criar mock local, sem Composio real;
9. criar painel visual somente leitura;
10. validar build/test;
11. não alterar o app instalado diretamente;
12. empacotar apenas após testes.

## Regras da fase futura
- Esta fase futura altera a UI.
- A fase atual não altera a UI.
- Qualquer build deve ocorrer em clone/fork, nunca no binário instalado.
- Rollback deve ser preservado.

## Observação
O plano acima é para uma fase futura segura; nesta fase apenas a visibilidade operacional por CLI/launcher foi auditada.
