#Requires -Version 5
param(
    [string]$ProjectName = "itam_validation",
    [string]$OutputDir = "backups",
    [string]$DatabaseName = "itam",
    [string]$ContainerService = "postgres"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$BackupRoot = Join-Path $Root $OutputDir
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupRoot "itam_backup_$Timestamp.dump"
$ManifestFile = Join-Path $BackupRoot "itam_backup_$Timestamp.manifest.json"
$ContainerBackupPath = "/tmp/itam_backup_$Timestamp.dump"

function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Command $($Arguments -join ' ')"
    }
}

New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null

Push-Location $Root
try {
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "ps", $ContainerService)
    $commandDescription = "docker compose -p $ProjectName exec -T $ContainerService sh -lc pg_dump -U itam -d $DatabaseName -Fc -f $ContainerBackupPath"
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "exec", "-T", $ContainerService, "sh", "-lc", "pg_dump -U itam -d $DatabaseName -Fc -f $ContainerBackupPath")
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "cp", "${ContainerService}:$ContainerBackupPath", $BackupFile)
    Invoke-Checked "docker" @("compose", "-p", $ProjectName, "exec", "-T", $ContainerService, "rm", "-f", $ContainerBackupPath)
    if (-not (Test-Path $BackupFile)) {
        throw "Backup file was not created: $BackupFile"
    }
    $size = (Get-Item $BackupFile).Length
    if ($size -le 0) {
        throw "Backup file is empty: $BackupFile"
    }
    $hash = (Get-FileHash -Path $BackupFile -Algorithm SHA256).Hash
    $manifest = [ordered]@{
        created_at = (Get-Date).ToUniversalTime().ToString("o")
        project_name = $ProjectName
        service = $ContainerService
        database = $DatabaseName
        backup_file = $BackupFile
        size_bytes = $size
        command = $commandDescription
        sha256 = $hash
        status = "created"
    }
    $manifest | ConvertTo-Json -Depth 4 | Set-Content -Path $ManifestFile -Encoding UTF8
    Write-Host "Backup created: $BackupFile"
    Write-Host "Manifest: $ManifestFile"
} finally {
    Pop-Location
}
