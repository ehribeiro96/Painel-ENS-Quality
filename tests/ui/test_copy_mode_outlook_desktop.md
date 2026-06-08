# Teste Manual - Modo `copy_mode=outlook_desktop`

## Objetivo
Validar que, no New Outlook Desktop (Windows), o fluxo de copia usa modo dedicado e nao aplica fallback degradado.

## Pre-condicoes
- Aplicacao reiniciada com a versao atual.
- Usuario de teste existente no portal.
- New Outlook Desktop aberto.

## Passos
1. Abrir o portal publico com:
   - `http://localhost:8090/assinaturas/?copy_mode=outlook_desktop`
2. Buscar colaborador por matricula ou e-mail.
3. Clicar em `Gerar`.
4. Clicar em `Copiar assinatura`.
5. Abrir New Outlook Desktop em:
   - `Configuracoes > Email > Criar e responder`.
6. Criar nova assinatura e colar (`Ctrl+V`) no editor.
7. Salvar, fechar e reabrir a tela de assinatura.

## Resultado esperado
- Nome, cargo, telefone, endereco e disclaimer mantem cor e tamanho do modelo.
- Link `ens.edu.br` permanece azul com tamanho visual correto.
- Nao ocorre conversao para estilos calculados no modo `outlook_desktop`.

## Cenário de falha dedicada
1. Repetir passos 1 a 4.
2. Simular falha de permissao de clipboard (politica do navegador/sistema).

## Resultado esperado em falha
- O sistema exibe erro claro de falha no modo dedicado.
- Nao executa fallback degradado de copia.
