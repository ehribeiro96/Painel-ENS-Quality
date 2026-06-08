#Requires -Version 5
param(
    [string]$ProjectName = "itam_validation",
    [Parameter(Mandatory = $true)][string]$BackupFile,
    [string]$DatabaseName = "itam",
    [string]$ContainerService = "postgres",
    [switch]$Force,
    [string]$BaseUrl = "http://127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ResolvedBackup = Resolve-Path $BackupFile
$ContainerBackupPath = "/tmp/itam_restore.dump"

function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Command $($Arguments -join ' ')"
    }
}

function Assert-Status {
    param([string]$Path, [int[]]$Expected)
    try {
        $response = Invoke-WebRequest -Uri "$BaseUrl$Path" -UseBasicParsing -MaximumRedirection 0 -TimeoutSec 15
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

function Wait-AppReady {
    $deadline = (Get-Date).AddSeconds(120)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri "$BaseUrl/health/ready" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) { return }
        } catch {
            Start-Sleep -Seconds 3
        }
    }
    throw "Application did not become ready after restore at $BaseUrl"
}

if (-not (Test-Path $ResolvedBackup)) {
    throw "Backup file not found: $BackupFile"
}

if (-not $Force) {
    $confirmation = Read-Host "Restore will replace database '$DatabaseName' in project '$ProjectName'. Type RESTORE $ProjectName to continue"
    if ($confirmation -ne "RESTORE $ProjectName") {
        throw "Restore cancelled."
    }
}

Push-Location $Root
try {
    Write-Host "Creating safety backup before restore..."
    & (Join-Path $PSScriptRoot "backup-db.ps1") -ProjectName $ProjectName -DatabaseName $DatabaseName -ContainerService $ContainerService -OutputDir "backups\pre_restore"
    if ($LASTEXITCODE -ne 0) {
        throw "Safety backup failed. Restore cancelled."
    }

    docker compose -p $ProjectName stop app | Out-Host
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "cp", "$ResolvedBackup", "${ContainerService}:$ContainerBackupPath")
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "exec", "-T", $ContainerService, "psql", "-U", "itam", "-d", "postgres", "-v", "ON_ERROR_STOP=1", "-c", "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DatabaseName' AND pid <> pg_backend_pid();")
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "exec", "-T", $ContainerService, "psql", "-U", "itam", "-d", "postgres", "-v", "ON_ERROR_STOP=1", "-c", "DROP DATABASE IF EXISTS $DatabaseName;")
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "exec", "-T", $ContainerService, "psql", "-U", "itam", "-d", "postgres", "-v", "ON_ERROR_STOP=1", "-c", "CREATE DATABASE $DatabaseName OWNER itam;")
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "exec", "-T", $ContainerService, "pg_restore", "-U", "itam", "-d", $DatabaseName, "--no-owner", "--no-privileges", $ContainerBackupPath)
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "exec", "-T", $ContainerService, "rm", "-f", $ContainerBackupPath)
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "start", "app")

    Wait-AppReady
    Assert-Status "/health" @(200)
    Assert-Status "/" @(200)
    Assert-Status "/assinaturas/" @(200)
    Assert-Status "/admin/" @(200, 302)
    Assert-Status "/api/v1/assets" @(401)
    Write-Host "Restore completed and smoke checks passed."
} finally {
    Pop-Location
}
