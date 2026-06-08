#Requires -Version 7
$ErrorActionPreference = "Stop"

# Diretorio onde o script esta (ops)
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Procura o diretorio do projeto integrado (contem run.py e backend/app/main.py)
$candidatos = @(
    (Join-Path $BaseDir "..\.."),
    (Join-Path $BaseDir "..\..\Portal-Assinatura-V2")
)

$ProjDir = $null
foreach ($c in $candidatos) {
    if ((Test-Path (Join-Path $c "run.py") -PathType Leaf -ErrorAction SilentlyContinue) -and
        (Test-Path (Join-Path $c "backend/app/main.py") -PathType Leaf -ErrorAction SilentlyContinue)) {
        $ProjDir = (Resolve-Path $c)
        break
    }
}

if (-not $ProjDir) {
    Write-Error "Nao consegui localizar o diretorio do projeto integrado (run.py + backend/app/main.py) acima de $BaseDir."
    exit 1
}

Set-Location $ProjDir

# Cria/usa o venv
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
$venvScripts = Join-Path (Resolve-Path ".venv") "Scripts"
$env:Path = "$venvScripts;$env:Path"

python -m pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r requirements-legacy.txt

# Carrega .env (.env, .env.local no projeto ou um nivel acima)
$envCandidates = @(
    (Join-Path $ProjDir ".env"),
    (Join-Path $ProjDir ".env.local"),
    (Join-Path (Split-Path $ProjDir -Parent) ".env")
)

foreach ($envFile in $envCandidates) {
    if (Test-Path $envFile) {
        foreach ($line in Get-Content $envFile) {
            if ($line -and -not $line.Trim().StartsWith("#")) {
                $kv = $line -split "=", 2
                if ($kv.Length -eq 2) {
                    [Environment]::SetEnvironmentVariable($kv[0].Trim(), $kv[1].Trim())
                }
            }
        }
        break
    }
}

python run.py
