---
id: "erro-instalacao-java"
title: "Erro de instalação ou atualização de Java"
document_type: "troubleshooting_note"
domain: "windows"
status: "draft"
risk_level: "medium"
owner: "Service Desk N2"
source_type: "internal_seed"
sensitivity: "sanitized"
automation_allowed: false
requires_admin: true
external_model_allowed: true
last_review: "2026-06-07"
version: 1
tags:
  - "java"
  - "jre"
  - "jdk"
  - "msi"
  - "path"
---

## Problema
Instalação ou atualização de Java falha na estação, impedindo execução de aplicações legadas ou ferramentas de desenvolvimento.

## Sintomas
- instalador encerra com erro genérico;
- aplicação continua usando versão antiga;
- variáveis PATH ou JAVA_HOME inconsistentes;
- coexistência 32 e 64 bits causa conflito.

## Perguntas mínimas
- Trata-se de JRE corporativo, JDK de desenvolvimento ou runtime embarcado?
- A aplicação exige versão específica?
- Há Java anterior instalado?
- A falha ocorre no instalador MSI ou somente no uso posterior?

## Evidências necessárias
- versão desejada;
- versão atual detectada;
- mensagem de erro do instalador;
- arquitetura do SO e da aplicação;
- variáveis de ambiente relevantes.

## Comandos seguros
```powershell
java -version
Get-Command java -ErrorAction SilentlyContinue
Get-ChildItem 'HKLM:\SOFTWARE\JavaSoft' -ErrorAction SilentlyContinue
Get-ChildItem 'HKLM:\SOFTWARE\WOW6432Node\JavaSoft' -ErrorAction SilentlyContinue
```

## Hipóteses
1. conflito entre múltiplas instalações;
2. PATH apontando para runtime antigo;
3. pacote incorreto para arquitetura;
4. pacote corporativo com pré-requisito ausente;
5. bloqueio por permissões ou antivírus.

## Resolução
1. Inventariar versões instaladas antes de remover qualquer runtime.
2. Confirmar requisito exato da aplicação.
3. Ajustar prioridade de PATH ou JAVA_HOME apenas com baseline documentado.
4. Se necessário, remover runtime obsoleto em janela autorizada e reinstalar pacote homologado.
5. Validar a chamada da aplicação específica após a instalação.

## Validação
- `java -version` retorna a versão esperada;
- aplicação alvo inicia;
- PATH e JAVA_HOME consistentes;
- não há regressão em outras aplicações dependentes.

## Rollback
- reinstalar versão anterior homologada;
- restaurar variáveis de ambiente anteriores se nova versão quebrar compatibilidade.

## Quando escalar
- pacote de software corporativo empacotado com erro;
- sistema legado exige combinação incomum de versões;
- impacto em aplicação crítica de produção.

## Macro ITIL sugerida
"Mapeadas versões Java presentes, requisito da aplicação e variáveis de ambiente, com correção controlada para restaurar execução sem introduzir conflito de runtimes."

## Riscos
- remover Java antigo pode quebrar aplicações legadas;
- PATH inconsistente gera falso sucesso em testes;
- misturar JRE e JDK sem requisito claro aumenta retrabalho.
