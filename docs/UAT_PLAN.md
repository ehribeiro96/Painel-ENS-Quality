# Plano de UAT Controlado

## Objetivo

Validar com usuários reais da TI se a plataforma ITAM permite operar os fluxos diários com segurança: localizar ativo, entender situação, movimentar, auditar, importar inventário pequeno e gerar assinatura.

## Escopo

- Login, logout e sessão autenticada.
- Dashboard operacional.
- Usuários, ativos, movimentações, histórico e auditoria.
- Importação Lansweeper via CSV pequeno.
- Assinatura corporativa pela API e legado `/assinaturas/`.
- Admin legado `/admin/` conforme comportamento atual.

## Fora de Escopo

- IA, Azure AD, Microsoft Graph, Lansweeper API.
- Novas telas grandes, novos módulos ou mudança de arquitetura.
- Teste de produção ou restore em produção.

## Participantes

- Administrador TI: valida cadastro, RBAC, auditoria e importação.
- Técnico de TI: valida ativos, busca, movimentação e histórico.
- Consulta/Viewer: valida leitura e bloqueio de escrita.
- Gestor: valida dashboard e consulta, se disponível.

## Pré-Requisitos

- Docker Desktop ativo.
- `ADMIN_EMAIL=estevao.quality@ens.edu.br`.
- `ADMIN_NAME=Estevão Ribeiro`.
- `ADMIN_PASSWORD` definido localmente em variável de ambiente ou `.env` não versionado.
- Porta `8080` livre.

## Acesso

Subir ambiente:

```powershell
$env:ADMIN_EMAIL="estevao.quality@ens.edu.br"
$env:ADMIN_PASSWORD="<DEFINIR_LOCALMENTE>"
$env:ADMIN_NAME="Estevão Ribeiro"
.\scripts\ops\start-uat.ps1
```

URL: `http://127.0.0.1:8080`

## Massa Inicial

Gerar dados controlados:

```powershell
.\scripts\ops\seed-uat-data.ps1
```

Dados usam prefixo `UAT`/`TEST` e e-mails `uat.*@ens.edu.br`.

## Como Reportar Erro

Registrar em `docs/UAT_FEEDBACK_FORM.md` ou ferramenta interna equivalente:

- Cenário testado.
- Resultado esperado e obtido.
- Evidência.
- Severidade percebida.
- Se bloqueia uso diário.

## Critérios de Aceite

- Usuário localiza ativo em poucos segundos.
- Técnico movimenta ativo com confirmação e histórico correto.
- Admin encontra log de auditoria da movimentação.
- Importação pequena exibe staging/conflitos/erros sem corromper inventário.
- Viewer não consegue escrever.
- Legado de assinaturas segue acessível.

## Critérios de Reprovação

- Login real falha.
- Movimentação não gera histórico/auditoria.
- Importação corrompe inventário.
- Viewer consegue escrever.
- Backup/restore não funciona no ambiente UAT.
- `/assinaturas/` quebra.

