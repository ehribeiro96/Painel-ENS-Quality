#Requires -Version 5
param(
    [string]$ProjectName = "itam_uat",
    [string]$BaseUrl = "http://127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")

function Assert-Env {
    param([string]$Name)
    if (-not [Environment]::GetEnvironmentVariable($Name)) {
        throw "$Name must be defined locally before starting UAT. Do not commit secrets."
    }
}

function Assert-UatPasswordPolicy {
    $password = [Environment]::GetEnvironmentVariable("ADMIN_PASSWORD")
    if ($password.Length -lt 10) {
        throw "ADMIN_PASSWORD must have at least 10 characters for UAT startup. The password was not printed."
    }
}

function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Command $($Arguments -join ' ')"
    }
}

function Wait-AppReady {
    param([string]$Url)
    $deadline = (Get-Date).AddSeconds(150)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri "$Url/health/ready" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) { return }
        } catch {
            Start-Sleep -Seconds 3
        }
    }
    throw "Application did not become ready at $Url"
}

function Show-AppDiagnostics {
    Write-Host ""
    Write-Host "Application did not become ready."
    Write-Host "See diagnostic output below."
    Write-Host "Likely startup failure in app container."
    Write-Host ""
    docker compose -p $ProjectName ps -a | Out-Host
    Write-Host ""
    docker compose -p $ProjectName logs app --no-color --tail=200 | Out-Host
    Write-Host ""
    $containerId = docker compose -p $ProjectName ps -q app
    if ($containerId) {
        docker inspect $containerId --format "ExitCode={{.State.ExitCode}} Status={{.State.Status}} Error={{.State.Error}} FinishedAt={{.State.FinishedAt}}" | Out-Host
    }
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

Assert-Env "ADMIN_EMAIL"
Assert-Env "ADMIN_PASSWORD"
Assert-Env "ADMIN_NAME"
Assert-UatPasswordPolicy

Push-Location $Root
try {
    Invoke-Checked "docker" @("--version")
    Invoke-Checked "docker" @("compose", "version")
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "up", "--build", "-d")
    try {
        Wait-AppReady $BaseUrl
    } catch {
        Show-AppDiagnostics
        throw "Application did not become ready. See diagnostic output above. Likely startup failure in app container."
    }

    Assert-Status "/health" @(200)
    Assert-Status "/" @(200)
    Assert-Status "/assinaturas/" @(200)
    Assert-Status "/admin/" @(200, 302)
    Assert-Status "/api/v1/assets" @(401)

    Write-Host ""
    Write-Host "UAT environment is ready."
    Write-Host "URL: $BaseUrl"
    Write-Host "Admin: $env:ADMIN_EMAIL"
    Write-Host "Senha: definida via ADMIN_PASSWORD local"
} finally {
    Pop-Location
}
