#Requires -Version 5
param(
    [switch]$Cleanup
)

$ErrorActionPreference = "Stop"

$ProjectName = "itam_validation"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$BaseUrl = $env:OPERATIONAL_BASE_URL
if (-not $BaseUrl) {
    $BaseUrl = "http://127.0.0.1:8080"
    $env:OPERATIONAL_BASE_URL = $BaseUrl
}
if (-not $env:ADMIN_EMAIL) {
    $env:ADMIN_EMAIL = "estevao.quality@ens.edu.br"
}
if (-not $env:ADMIN_NAME) {
    $env:ADMIN_NAME = "Estevão Ribeiro"
}
if (-not $env:ADMIN_PASSWORD) {
    throw "ADMIN_PASSWORD must be defined locally before running operational validation. Do not commit it."
}

function Invoke-RequiredCommand {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Command $($Arguments -join ' ')"
    }
}

function Wait-AppReady {
    param([string]$Url)
    $deadline = (Get-Date).AddSeconds(120)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri "$Url/health/ready" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                return
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "Application did not become ready at $Url"
}

function Assert-Status {
    param([string]$Path, [int[]]$Expected)
    try {
        $response = Invoke-WebRequest -Uri "$BaseUrl$Path" -UseBasicParsing -MaximumRedirection 0 -TimeoutSec 10
        $status = [int]$response.StatusCode
    } catch {
        if ($_.Exception.Response) {
            $status = [int]$_.Exception.Response.StatusCode
        } else {
            throw
        }
    }
    if ($Expected -notcontains $status) {
        throw "Unexpected status for $Path. Expected $($Expected -join '/') got $status"
    }
    Write-Host "$Path -> $status"
}

Push-Location $Root
try {
    Invoke-RequiredCommand "docker" @("--version")
    Invoke-RequiredCommand "docker" @("compose", "version")
    Invoke-RequiredCommand "docker" @("compose", "-p", $ProjectName, "up", "--build", "-d")
    Wait-AppReady $BaseUrl

    Assert-Status "/health" @(200)
    Assert-Status "/" @(200)
    Assert-Status "/assinaturas/" @(200)
    Assert-Status "/admin/" @(200, 302)
    Assert-Status "/api/v1/assets" @(401)

    $python = "python"
    if (Test-Path ".\.venv\Scripts\python.exe") {
        $python = ".\.venv\Scripts\python.exe"
    }
    Invoke-RequiredCommand $python @("-m", "compileall", "-q", "backend\app", "backend\alembic")
    Invoke-RequiredCommand $python @("-m", "unittest", "discover", "-s", "tests")

    Push-Location "frontend\itam-platform"
    try {
        Invoke-RequiredCommand "npm" @("run", "build")
    } finally {
        Pop-Location
    }

    Invoke-RequiredCommand "docker" @("compose", "-p", $ProjectName, "exec", "-T", "app", "sh", "-lc", "cd /app/backend && alembic current && alembic heads")

    Write-Host "Operational validation completed successfully."
} finally {
    if ($Cleanup) {
        docker compose -p $ProjectName down -v --remove-orphans | Out-Host
    }
    Pop-Location
}
