#Requires -Version 5
param(
    [string]$ProjectName = "itam_uat",
    [switch]$StopOnly,
    [switch]$RemoveContainers,
    [switch]$RemoveVolumes
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")

if (-not $StopOnly -and -not $RemoveContainers -and -not $RemoveVolumes) {
    $StopOnly = $true
}

Push-Location $Root
try {
    if ($RemoveVolumes) {
        $confirmation = Read-Host "Type REMOVE UAT VOLUMES to delete containers and volumes for project $ProjectName"
        if ($confirmation -ne "REMOVE UAT VOLUMES") {
            throw "Volume removal cancelled."
        }
        docker compose -p $ProjectName down -v --remove-orphans | Out-Host
        exit $LASTEXITCODE
    }

    if ($RemoveContainers) {
        docker compose -p $ProjectName down --remove-orphans | Out-Host
        exit $LASTEXITCODE
    }

    docker compose -p $ProjectName stop | Out-Host
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
