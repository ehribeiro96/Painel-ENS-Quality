# Projeto unico, hibrido (Linux + Windows) - Portal-Assinatura-V2

Este bundle vira **um unico projeto** rodando do mesmo jeito em Linux e Windows, agora somente com FastAPI + React.

## O que foi adicionado
- `run.py` - **entrypoint unico** (uvicorn com `fastapi_app:app`).
- `.env.example` (repo raiz) - modelo de variaveis.
- `ops/start_linux.sh`, `ops/start_windows.ps1`, `ops/install_windows_service.ps1` - scripts de operacao.
- `Dockerfile`, `docker-compose.yml` na raiz - execucao containerizada em qualquer SO.

## Como rodar (bare metal)
Crie `.env` na raiz (baseado em `.env.example`) e rode:
- **Linux**: `./ops/start_linux.sh`
- **Windows (PowerShell 7)**: `./ops/start_windows.ps1`

## Servico no Windows
```
pwsh -File .\ops\install_windows_service.ps1 -TaskName PortalAssinatura -User SYSTEM
```

## Docker
```
docker compose build
docker compose up -d
```

Pronto: **um projeto unico** que funciona em ambiente hibrido.

## Configuracao rapida via variaveis de ambiente

Exemplos de variaveis usadas pelo portal:

```bash
# Caminho do banco de dados
export ENS_DB_PATH="/caminho/para/ens.db"

# Tipo de aplicacao: 'admin' ou 'publico'
export ENS_APP_MODE="admin"

# Modo de envio de e-mail (hibrido)
# ON  -> forca SMTP
# OFF -> usa Microsoft Graph
export ENS_SMTP_MODE="ON"

# Servidor SMTP utilizado para envio em homologacao
export ENS_SMTP_HOST="smtp.office365.com"
export ENS_SMTP_PORT="587"

# Credenciais da conta de envio em homologacao
export ENS_SMTP_USER="<DEFINIR_LOCALMENTE>"
export ENS_SMTP_PASSWORD="<SMTP_PASSWORD_REDACTED>"
```
