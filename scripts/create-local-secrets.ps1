# Execute in project root (PowerShell)
mkdir .\secrets -ErrorAction SilentlyContinue
if (-not (Test-Path .\secrets\ens_secret_key)) {
    [Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 })) | Out-File -Encoding utf8 .\secrets\ens_secret_key
}
if (-not (Test-Path .\secrets\ms_client_id)) {
    "<DEFINIR_LOCALMENTE>" | Out-File -Encoding utf8 .\secrets\ms_client_id
}
if (-not (Test-Path .\secrets\ms_client_secret)) {
    "<DEFINIR_LOCALMENTE>" | Out-File -Encoding utf8 .\secrets\ms_client_secret
}
Write-Host "Local secret placeholders created under .\secrets. Do not commit this directory."
