#Requires -Version 5
param(
    [string]$BaseUrl = "http://127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")

if (-not $env:ADMIN_EMAIL -or -not $env:ADMIN_PASSWORD) {
    throw "ADMIN_EMAIL and ADMIN_PASSWORD must be defined locally. Do not commit secrets."
}

function Invoke-Api {
    param([string]$Method, [string]$Path, [hashtable]$Headers, [object]$Body = $null)
    $params = @{
        Method = $Method
        Uri = "$BaseUrl/api/v1$Path"
        Headers = $Headers
        TimeoutSec = 30
    }
    if ($null -ne $Body) {
        $params.Body = ($Body | ConvertTo-Json -Depth 6)
        $params.ContentType = "application/json"
    }
    Invoke-RestMethod @params
}

try {
    $login = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/auth/login" -ContentType "application/json" -Body (@{
        email = $env:ADMIN_EMAIL
        password = $env:ADMIN_PASSWORD
    } | ConvertTo-Json)
} catch {
    throw "Admin login failed during UAT seed. If the UAT volume already existed, use the password that created the admin or explicitly recreate the UAT volume after backup. The password was not printed."
}
$headers = @{ Authorization = "Bearer $($login.access_token)" }

function Get-OrCreateUser {
    param([string]$Name, [string]$Email, [string]$Role)
    $existing = Invoke-Api -Method Get -Path "/users?page_size=100&search=$Email" -Headers $headers
    foreach ($item in $existing.items) {
        if ($item.email -eq $Email) { return $item }
    }
    Invoke-Api -Method Post -Path "/users" -Headers $headers -Body @{
        name = $Name
        email = $Email
        role = $Role
        status = "ACTIVE"
        department = "TI"
        business_unit = "Matriz"
        job_title = "UAT"
    }
}

function Get-OrCreateAsset {
    param([hashtable]$Payload)
    $search = [uri]::EscapeDataString($Payload.hostname)
    $existing = Invoke-Api -Method Get -Path "/assets?page_size=100&search=$search" -Headers $headers
    foreach ($item in $existing.items) {
        if ($item.hostname -eq $Payload.hostname) { return $item }
    }
    Invoke-Api -Method Post -Path "/assets" -Headers $headers -Body $Payload
}

$collab = Get-OrCreateUser "UAT Colaborador Teste" "uat.colaborador.teste@ens.edu.br" "VIEWER"
$gestor = Get-OrCreateUser "UAT Gestor Teste" "uat.gestor.teste@ens.edu.br" "MANAGER"
$tech = Get-OrCreateUser "UAT Técnico Teste" "uat.tecnico.teste@ens.edu.br" "TECHNICIAN"
$viewer = Get-OrCreateUser "UAT Viewer Teste" "uat.viewer.teste@ens.edu.br" "VIEWER"

$assets = @(
    @{ hostname = "RJMTEST001"; patrimony = "PAT-UAT-001"; serial = "SN-UAT-001"; manufacturer = "Dell"; model = "Latitude"; asset_type = "NOTEBOOK"; status = "IN_USE"; location = "Matriz"; current_user_id = $collab.id },
    @{ hostname = "RJMTEST002"; patrimony = "PAT-UAT-002"; serial = "SN-UAT-002"; manufacturer = "Dell"; model = "OptiPlex"; asset_type = "DESKTOP"; status = "STOCK"; location = "Estoque TI" },
    @{ hostname = "RJMTEST003"; patrimony = "PAT-UAT-003"; serial = "SN-UAT-003"; manufacturer = "LG"; model = "24MP"; asset_type = "MONITOR"; status = "STOCK"; location = "Estoque TI" },
    @{ hostname = "RJMTEST004"; patrimony = "PAT-UAT-004"; serial = "SN-UAT-004"; manufacturer = "HP"; model = "EliteBook"; asset_type = "NOTEBOOK"; status = "MAINTENANCE"; location = "Laboratório TI" },
    @{ hostname = "RJMTEST005"; patrimony = "PAT-UAT-005"; serial = "SN-UAT-005"; manufacturer = "Lenovo"; model = "ThinkPad"; asset_type = "NOTEBOOK"; status = "DEFECTIVE"; location = "Triagem TI" }
)

foreach ($payload in $assets) {
    Get-OrCreateAsset $payload | Out-Null
}

$movable = Get-OrCreateAsset @{ hostname = "RJMTEST002"; patrimony = "PAT-UAT-002"; serial = "SN-UAT-002"; manufacturer = "Dell"; model = "OptiPlex"; asset_type = "DESKTOP"; status = "STOCK"; location = "Estoque TI" }
$history = Invoke-Api -Method Get -Path "/assets/$($movable.id)/history" -Headers $headers
if ($history.Count -eq 0) {
    Invoke-Api -Method Post -Path "/assets/$($movable.id)/move" -Headers $headers -Body @{ new_user_id = $tech.id; new_status = "IN_USE"; new_location = "Matriz"; justification = "UAT estoque para técnico"; notes = "Seed UAT" } | Out-Null
    Invoke-Api -Method Post -Path "/assets/$($movable.id)/move" -Headers $headers -Body @{ new_status = "MAINTENANCE"; new_location = "Laboratório TI"; justification = "UAT envio para manutenção"; notes = "Seed UAT" } | Out-Null
    Invoke-Api -Method Post -Path "/assets/$($movable.id)/move" -Headers $headers -Body @{ new_status = "STOCK"; new_location = "Estoque TI"; justification = "UAT retorno para estoque"; notes = "Seed UAT" } | Out-Null
}

function Submit-ImportFixture {
    param([string]$FixtureName)
    $jobs = Invoke-Api -Method Get -Path "/imports?page_size=100" -Headers $headers
    foreach ($job in $jobs.items) {
        if ($job.filename -eq $FixtureName) { return }
    }
    $fixturePath = Join-Path $Root "tests\fixtures\imports\$FixtureName"
    if (-not (Test-Path $fixturePath)) {
        Write-Host "Import fixture not found, skipping: $fixturePath"
        return
    }
    curl.exe -sS -X POST "$BaseUrl/api/v1/imports/lansweeper" `
        -H "Authorization: Bearer $($login.access_token)" `
        -F "file=@$fixturePath;type=text/csv" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upload import fixture $FixtureName"
    }
}

Submit-ImportFixture "lansweeper_valid.csv"
Submit-ImportFixture "lansweeper_duplicate.csv"
Submit-ImportFixture "lansweeper_invalid.csv"

Write-Host "UAT seed completed. Users: $($collab.email), $($gestor.email), $($tech.email), $($viewer.email)"
