#Requires -Version 5
param(
    [string]$ProjectName = "itam_uat",
    [string]$BaseUrl = "http://127.0.0.1:8080",
    [string]$EvidenceRoot = "uat_evidence"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$SessionId = Get-Date -Format "yyyyMMdd_HHmmss"
$SessionDir = Join-Path $Root (Join-Path $EvidenceRoot $SessionId)

function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Command $($Arguments -join ' ')"
    }
}

function Assert-Env {
    param([string]$Name)
    if (-not [Environment]::GetEnvironmentVariable($Name)) {
        throw "$Name must be defined locally before UAT. Do not commit secrets."
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
    @{ path = $Path; status = $status; expected = $Expected }
}

function Ensure-GitIgnoreEntry {
    param([string]$Entry)
    $gitignore = Join-Path $Root ".gitignore"
    if (-not (Test-Path $gitignore)) {
        New-Item -ItemType File -Path $gitignore | Out-Null
    }
    $content = Get-Content $gitignore -ErrorAction SilentlyContinue
    if ($content -notcontains $Entry) {
        Add-Content -Path $gitignore -Value $Entry
    }
}

Assert-Env "ADMIN_EMAIL"
Assert-Env "ADMIN_PASSWORD"
Assert-Env "ADMIN_NAME"

Push-Location $Root
try {
    New-Item -ItemType Directory -Force -Path $SessionDir | Out-Null
    Ensure-GitIgnoreEntry "$EvidenceRoot/"

    Invoke-Checked "docker" @("--version")
    Invoke-Checked "docker" @("compose", "version")
    $services = docker compose config --services
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose config failed"
    }

    & (Join-Path $PSScriptRoot "start-uat.ps1") -ProjectName $ProjectName -BaseUrl $BaseUrl
    if ($LASTEXITCODE -ne 0) { throw "start-uat.ps1 failed" }

    & (Join-Path $PSScriptRoot "seed-uat-data.ps1") -BaseUrl $BaseUrl
    if ($LASTEXITCODE -ne 0) { throw "seed-uat-data.ps1 failed" }

    $backupBefore = Get-ChildItem -Path (Join-Path $Root "backups") -Filter "*.manifest.json" -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    & (Join-Path $PSScriptRoot "backup-db.ps1") -ProjectName $ProjectName
    if ($LASTEXITCODE -ne 0) { throw "backup-db.ps1 failed" }
    $backupAfter = Get-ChildItem -Path (Join-Path $Root "backups") -Filter "*.manifest.json" -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $backupAfter -or ($backupBefore -and $backupAfter.FullName -eq $backupBefore.FullName)) {
        throw "Initial backup manifest was not created"
    }

    $smoke = @(
        Assert-Status "/health" @(200)
        Assert-Status "/" @(200)
        Assert-Status "/assinaturas/" @(200)
        Assert-Status "/admin/" @(200, 302)
        Assert-Status "/api/v1/assets" @(401)
    )

    $commitHash = $null
    try {
        $commitHash = (git rev-parse HEAD 2>$null)
        if ($LASTEXITCODE -ne 0) { $commitHash = $null }
    } catch {
        $commitHash = $null
    }

    $manifest = [ordered]@{
        session_id = $SessionId
        created_at = (Get-Date).ToUniversalTime().ToString("o")
        project_name = $ProjectName
        url = $BaseUrl
        admin_email = $env:ADMIN_EMAIL
        evidence_dir = $SessionDir
        docker_services = @($services)
        initial_backup_manifest = $backupAfter.FullName
        smoke_result = $smoke
        scripts_executed = @("start-uat.ps1", "seed-uat-data.ps1", "backup-db.ps1")
        commit_hash = $commitHash
        observations = "ADMIN_PASSWORD was provided locally and was not printed."
    }
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $SessionDir "session_manifest.json") -Encoding UTF8

    Copy-Item "docs\templates\uat_results_template.csv" (Join-Path $SessionDir "uat_results.csv") -Force
    Copy-Item "docs\templates\uat_known_issues_template.csv" (Join-Path $SessionDir "uat_known_issues.csv") -Force

    Write-Host "UAT session prepared."
    Write-Host "SessionDir: $SessionDir"
    Write-Host "URL: $BaseUrl"
    Write-Host "Admin: $env:ADMIN_EMAIL"
    Write-Host "Password: defined locally and not printed"
} finally {
    Pop-Location
}
