#Requires -Version 5
param(
    [Parameter(Mandatory = $true)][string]$SessionDir,
    [string]$ProjectName = "itam_uat",
    [string]$BaseUrl = "http://127.0.0.1:8080",
    [switch]$StopOnly,
    [switch]$RemoveContainers,
    [switch]$RemoveVolumes,
    [switch]$SkipTests,
    [switch]$SkipBackup
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ResolvedSessionDir = Resolve-Path $SessionDir

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
    @{ path = $Path; status = $status; expected = $Expected }
}

function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Command $($Arguments -join ' ')"
    }
}

Push-Location $Root
try {
    $finalBackupManifest = $null
    if (-not $SkipBackup) {
        & (Join-Path $PSScriptRoot "backup-db.ps1") -ProjectName $ProjectName
        if ($LASTEXITCODE -ne 0) { throw "Final backup failed" }
        $finalBackupManifest = (Get-ChildItem -Path (Join-Path $Root "backups") -Filter "*.manifest.json" -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
    }

    $smoke = @(
        Assert-Status "/health" @(200)
        Assert-Status "/" @(200)
        Assert-Status "/assinaturas/" @(200)
        Assert-Status "/admin/" @(200, 302)
        Assert-Status "/api/v1/assets" @(401)
    )

    $testResult = "skipped"
    if (-not $SkipTests) {
        $env:OPERATIONAL_BASE_URL = $BaseUrl
        $env:OPERATIONAL_PROJECT_NAME = $ProjectName
        $python = "python"
        if (Test-Path ".\.venv\Scripts\python.exe") {
            $python = ".\.venv\Scripts\python.exe"
        }
        & $python -m unittest discover -s tests | Out-Host
        if ($LASTEXITCODE -ne 0) {
            $testResult = "failed"
            throw "Regression suite failed"
        }
        $testResult = "passed"
    }

    $summary = [ordered]@{
        finished_at = (Get-Date).ToUniversalTime().ToString("o")
        project_name = $ProjectName
        url = $BaseUrl
        final_backup_manifest = $finalBackupManifest
        smoke_result = $smoke
        regression_result = $testResult
        stop_action = if ($RemoveVolumes) { "RemoveVolumes" } elseif ($RemoveContainers) { "RemoveContainers" } elseif ($StopOnly) { "StopOnly" } else { "NotStopped" }
        observations = "ADMIN_PASSWORD was not printed."
    }
    $summary | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $ResolvedSessionDir "final_summary.json") -Encoding UTF8

    if ($RemoveVolumes) {
        & (Join-Path $PSScriptRoot "stop-uat.ps1") -ProjectName $ProjectName -RemoveVolumes
    } elseif ($RemoveContainers) {
        & (Join-Path $PSScriptRoot "stop-uat.ps1") -ProjectName $ProjectName -RemoveContainers
    } elseif ($StopOnly) {
        & (Join-Path $PSScriptRoot "stop-uat.ps1") -ProjectName $ProjectName -StopOnly
    } else {
        $answer = Read-Host "Stop UAT environment now? Type StopOnly, RemoveContainers, RemoveVolumes or KeepRunning"
        if ($answer -eq "StopOnly") {
            & (Join-Path $PSScriptRoot "stop-uat.ps1") -ProjectName $ProjectName -StopOnly
        } elseif ($answer -eq "RemoveContainers") {
            & (Join-Path $PSScriptRoot "stop-uat.ps1") -ProjectName $ProjectName -RemoveContainers
        } elseif ($answer -eq "RemoveVolumes") {
            & (Join-Path $PSScriptRoot "stop-uat.ps1") -ProjectName $ProjectName -RemoveVolumes
        }
    }

    Write-Host "UAT session finished."
    Write-Host "Summary: $(Join-Path $ResolvedSessionDir 'final_summary.json')"
} finally {
    Pop-Location
}
