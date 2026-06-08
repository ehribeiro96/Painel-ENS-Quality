param(
    [string]$DryRunReportPath,
    [switch]$AllowUnmaskedLocalReview,
    [string]$OutputPath = "docs/LEGACY_ENS_DB_PRE_APPLY_REVIEW.md"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path

function Get-LatestDryRunReport {
    $reportDir = Join-Path $ProjectRoot "uat_evidence\legacy_ens_db_import"
    if (-not (Test-Path -LiteralPath $reportDir)) {
        throw "DryRun report directory not found: $reportDir"
    }

    $latest = Get-ChildItem -LiteralPath $reportDir -Filter "legacy_ens_db_dryrun_*.json" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $latest) {
        throw "No DryRun report found in $reportDir"
    }

    return $latest.FullName
}

function Mask-Email {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value) -or -not $Value.Contains("@")) {
        return "<empty_or_invalid>"
    }
    $parts = $Value.Split("@", 2)
    $local = $parts[0]
    $domain = $parts[1]
    if ($local.Length -le 2) {
        return "***@$domain"
    }
    return "$($local.Substring(0, 2))***@$domain"
}

function Mask-Name {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return "<empty>"
    }
    $tokens = $Value -split "\s+" | Where-Object { $_ }
    if (-not $tokens) {
        return "<empty>"
    }
    $masked = foreach ($token in ($tokens | Select-Object -First 2)) {
        if ($token.Length -le 2) { "***" } else { "$($token.Substring(0, 2))***" }
    }
    return ($masked -join " ")
}

function Escape-Markdown {
    param([object]$Value)
    if ($null -eq $Value) {
        return "-"
    }
    $text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($text)) {
        return "-"
    }
    return $text.Replace("|", "\|").Replace("`r", " ").Replace("`n", " ")
}

function Find-Python {
    $localPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $localPython) {
        return $localPython
    }
    throw "No usable project Python found at $localPython"
}

function Get-EnrichedReview {
    param(
        [string]$ReportPath,
        [bool]$AllowUnmasked
    )

    $python = Find-Python
    $allowValue = if ($AllowUnmasked) { "1" } else { "0" }

    $code = @'
import asyncio
import importlib.util
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

report_path = Path(os.environ["PRE_APPLY_REPORT_PATH"])
allow_unmasked = os.environ.get("PRE_APPLY_ALLOW_UNMASKED") == "1"
root = Path(os.environ["PRE_APPLY_PROJECT_ROOT"])
script = root / "scripts" / "import_legacy_ens_db_to_postgres.py"

def mask_email(value):
    value = (value or "").strip()
    if "@" not in value:
        return "<empty_or_invalid>"
    local, domain = value.split("@", 1)
    if len(local) <= 2:
        return f"***@{domain}"
    return f"{local[:2]}***@{domain}"

def mask_name(value):
    value = (value or "").strip()
    if not value:
        return "<empty>"
    parts = value.split()
    return " ".join((part[:2] + "***") if len(part) > 2 else "***" for part in parts[:2])

def mask_login(value):
    value = (value or "").strip()
    if not value:
        return "<empty>"
    if allow_unmasked:
        return value
    return (value[:2] + "***") if len(value) > 2 else "***"

def maybe_email(value):
    return value if allow_unmasked else mask_email(value)

def maybe_name(value):
    return value if allow_unmasked else mask_name(value)

def value_of(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None

payload = {
    "updates": [],
    "duplicate_logins": [],
    "warnings": [],
    "errors": [],
    "can_enrich": False,
}

try:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    sqlite_path = Path(report.get("sqlite_path") or "")
    if not sqlite_path.exists():
        payload["warnings"].append("SQLite source path from DryRun report was not available for detail enrichment.")
        print(json.dumps(payload, ensure_ascii=False))
        raise SystemExit(0)

    spec = importlib.util.spec_from_file_location("legacy_importer_pre_apply", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["legacy_importer_pre_apply"] = module
    spec.loader.exec_module(module)
    candidates, _inventory = module.read_candidates(sqlite_path)
    payload["can_enrich"] = True

    grouped = defaultdict(list)
    for candidate in candidates:
        login = value_of(candidate.login_hint)
        if login:
            grouped[login.lower()].append(candidate)
    for login, group in sorted(grouped.items()):
        if len(group) > 1:
            payload["duplicate_logins"].append({
                "login": mask_login(login),
                "count": len(group),
                "emails": [maybe_email(item.email) for item in group],
                "recommendation": "Documentar como hint/metadado; e-mail permanece identidade primaria.",
            })

    if not os.environ.get("DATABASE_URL"):
        payload["warnings"].append("DATABASE_URL is not set; update details could not be compared with PostgreSQL.")
        print(json.dumps(payload, ensure_ascii=False))
        raise SystemExit(0)

    from sqlalchemy import func, select
    from app.domains.users.models import User

    risk_fields = {
        "password", "senha", "password_hash", "hash", "role", "roles", "perfil",
        "permissions", "rbac", "status", "eh_admin", "is_admin", "must_change",
    }
    sensitive_emails = {"estevao.quality@ens.edu.br", "admin@example.com"}

    async def main():
        async with module.AsyncSessionLocal() as session:
            for candidate in candidates:
                if not candidate.valid:
                    continue
                existing = (
                    await session.execute(
                        select(User).where(func.lower(User.email) == candidate.email.lower())
                    )
                ).scalar_one_or_none()
                if existing is None:
                    continue

                changed = []
                preserved = []
                for attr in ("name", "job_title", "department", "business_unit", "manager_name", "phone"):
                    incoming = value_of(getattr(candidate, attr, None))
                    current = value_of(getattr(existing, attr, None))
                    if incoming and not current:
                        changed.append(attr)
                    elif current:
                        preserved.append(attr)

                if not value_of(getattr(existing, "source", None)):
                    changed.append("source")
                changed.append("source_metadata")

                role = str(getattr(existing, "role", "") or "")
                status = str(getattr(existing, "status", "") or "")
                email_lower = candidate.email.lower()
                risks = []
                if role.upper().endswith("ADMIN") or role.upper() == "ADMIN":
                    risks.append("existing_user_has_admin_role")
                if email_lower in sensitive_emails:
                    risks.append("sensitive_admin_email")
                for field in changed:
                    if field.lower() in risk_fields:
                        risks.append(f"risky_field_change:{field}")

                payload["updates"].append({
                    "email": maybe_email(candidate.email),
                    "current_name": maybe_name(getattr(existing, "name", "")),
                    "legacy_name": maybe_name(candidate.name),
                    "role": role,
                    "status": status,
                    "fields_to_update": changed,
                    "fields_to_preserve": preserved,
                    "risk": "; ".join(sorted(set(risks))) if risks else "LOW",
                    "recommendation": "Bloquear Apply ate revisao humana deste usuario." if risks else "Revisar e aprovar antes do Apply.",
                })

        print(json.dumps(payload, ensure_ascii=False))

    asyncio.run(main())
except SystemExit:
    raise
except Exception as exc:
    payload["errors"].append(f"{type(exc).__name__}: {exc}")
    print(json.dumps(payload, ensure_ascii=False))
'@

    $env:PRE_APPLY_REPORT_PATH = $ReportPath
    $env:PRE_APPLY_ALLOW_UNMASKED = $allowValue
    $env:PRE_APPLY_PROJECT_ROOT = $ProjectRoot
    try {
        $json = $code | & $python -
        if (-not $json) {
            throw "Enrichment helper produced no output."
        }
        return ($json | ConvertFrom-Json)
    } finally {
        Remove-Item Env:\PRE_APPLY_REPORT_PATH -ErrorAction SilentlyContinue
        Remove-Item Env:\PRE_APPLY_ALLOW_UNMASKED -ErrorAction SilentlyContinue
        Remove-Item Env:\PRE_APPLY_PROJECT_ROOT -ErrorAction SilentlyContinue
    }
}

function Get-Decision {
    param(
        [object]$Report,
        [object]$Enriched
    )

    $result = $Report.postgres_result
    if (-not $result) {
        return "BLOCKED_FOR_APPLY"
    }
    if (($result.failures -as [int]) -gt 0 -or ($result.invalid -as [int]) -gt 0) {
        return "BLOCKED_FOR_APPLY"
    }
    $sensitiveSkipped = ($result.sensitive_updates_skipped -as [int]) -gt 0
    $plannedUpdates = if ($null -ne $result.planned_updates) { $result.planned_updates -as [int] } else { $result.updated -as [int] }
    if ($sensitiveSkipped -and $plannedUpdates -eq 0 -and [bool]$result.ready_for_apply) {
        return "APPROVED_WITH_WARNINGS"
    }
    foreach ($update in @($Enriched.updates)) {
        if ([string]$update.risk -ne "LOW") {
            return "BLOCKED_FOR_APPLY"
        }
    }
    if ($plannedUpdates -gt 0 -or ($Report.inventory.quality.duplicate_logins -as [int]) -gt 0 -or $sensitiveSkipped) {
        return "APPROVED_WITH_WARNINGS"
    }
    return "APPROVED_FOR_APPLY"
}

function Add-TableRow {
    param([object[]]$Values)
    return "| " + (($Values | ForEach-Object { Escape-Markdown $_ }) -join " | ") + " |"
}

$resolvedReport = if ($DryRunReportPath) {
    (Resolve-Path -LiteralPath $DryRunReportPath).Path
} else {
    Get-LatestDryRunReport
}

$dryRun = Get-Content -LiteralPath $resolvedReport -Raw | ConvertFrom-Json
if ($dryRun.mode -ne "DryRun") {
    throw "Report mode must be DryRun. Actual mode: $($dryRun.mode)"
}

$enriched = Get-EnrichedReview -ReportPath $resolvedReport -AllowUnmasked ([bool]$AllowUnmaskedLocalReview)
$decision = Get-Decision -Report $dryRun -Enriched $enriched
$reviewedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")

$result = $dryRun.postgres_result
$quality = $dryRun.inventory.quality
$sensitiveDiscarded = @($dryRun.inventory.sensitive_fields_discarded)

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Revisao Pre-Apply - Legacy ENS DB")
$lines.Add("")
$lines.Add("## Resumo executivo")
$lines.Add("")
$lines.Add("- Relatorio DryRun analisado: ``$resolvedReport``")
$lines.Add("- Data/hora da revisao: $reviewedAt")
$lines.Add("- Decisao preliminar: **$decision**")
$lines.Add("- Apply executado nesta etapa: **nao**")
$lines.Add("- Confirmacao ``APPLY_LEGACY_ENS_DB`` usada nesta etapa: **nao**")
$lines.Add("")

$lines.Add("## Resumo do DryRun")
$lines.Add("")
$lines.Add("| Metrica | Valor |")
$lines.Add("| --- | ---: |")
$lines.Add((Add-TableRow @("total lido", $result.total_read)))
$lines.Add((Add-TableRow @("candidatos validos", $result.valid_candidates)))
$lines.Add((Add-TableRow @("previstos para criacao", $result.created)))
$plannedUpdatesValue = if ($null -ne $result.planned_updates) { $result.planned_updates } else { $result.updated }
$sensitiveSkippedValue = if ($null -ne $result.sensitive_updates_skipped) { $result.sensitive_updates_skipped } else { 0 }
$lines.Add((Add-TableRow @("previstos para atualizacao aplicavel", $plannedUpdatesValue)))
$lines.Add((Add-TableRow @("updates sensiveis ignorados", $sensitiveSkippedValue)))
$lines.Add((Add-TableRow @("invalidos", $result.invalid)))
$lines.Add((Add-TableRow @("sem e-mail", $result.without_email)))
$lines.Add((Add-TableRow @("sem nome", $result.without_name)))
$lines.Add((Add-TableRow @("duplicados por e-mail", $quality.duplicate_emails)))
$lines.Add((Add-TableRow @("duplicados por matricula/login", $quality.duplicate_logins)))
$lines.Add((Add-TableRow @("falhas", $result.failures)))
$lines.Add("")

$lines.Add("## Contas sensiveis ignoradas pela politica")
$lines.Add("")
if (@($result.skipped_sensitive_accounts).Count -eq 0) {
    $lines.Add("Nenhuma conta sensivel foi marcada como skipped pelo DryRun.")
} else {
    $lines.Add("| E-mail | Nome atual | Nome legado | Campos que seriam atualizados | Motivo | Decisao |")
    $lines.Add("| --- | --- | --- | --- | --- | --- |")
    foreach ($skipped in @($result.skipped_sensitive_accounts)) {
        $lines.Add((Add-TableRow @(
            $skipped.email,
            $skipped.current_name,
            $skipped.legacy_name,
            (@($skipped.fields_that_would_update) -join ", "),
            $skipped.reason,
            $skipped.decision
        )))
    }
    $lines.Add("")
    $lines.Add("Essas contas nao serao atualizadas automaticamente no Apply enquanto a politica estiver ativa.")
}
$lines.Add("")

$lines.Add("## Usuario previsto para atualizacao")
$lines.Add("")
if (@($enriched.updates).Count -eq 0 -or (($result.sensitive_updates_skipped -as [int]) -gt 0 -and ($plannedUpdatesValue -as [int]) -eq 0)) {
    $lines.Add("Nenhum usuario existente foi identificado para atualizacao, ou os detalhes nao puderam ser enriquecidos.")
} else {
    $lines.Add("| E-mail | Nome atual | Nome legado | Campos que seriam atualizados | Campos preservados | Risco | Recomendacao |")
    $lines.Add("| --- | --- | --- | --- | --- | --- | --- |")
    foreach ($update in @($enriched.updates)) {
        $lines.Add((Add-TableRow @(
            $update.email,
            $update.current_name,
            $update.legacy_name,
            (@($update.fields_to_update) -join ", "),
            (@($update.fields_to_preserve) -join ", "),
            $update.risk,
            $update.recommendation
        )))
    }
}
$lines.Add("")

$lines.Add("## Duplicidades por matricula/login")
$lines.Add("")
if (@($enriched.duplicate_logins).Count -eq 0) {
    $lines.Add("Nenhuma duplicidade por matricula/login foi detalhada.")
} else {
    $lines.Add("| Matricula/Login | Ocorrencias | E-mails | Decisao recomendada |")
    $lines.Add("| --- | ---: | --- | --- |")
    foreach ($duplicate in @($enriched.duplicate_logins)) {
        $lines.Add((Add-TableRow @(
            $duplicate.login,
            $duplicate.count,
            (@($duplicate.emails) -join ", "),
            $duplicate.recommendation
        )))
    }
}
$lines.Add("")
$lines.Add("Regra aplicada: e-mail e a identidade primaria; matricula/login permanece apenas como hint/metadado.")
$lines.Add("")

$lines.Add("## Seguranca")
$lines.Add("")
$lines.Add("- Apply nao foi executado.")
$lines.Add("- A confirmacao ``APPLY_LEGACY_ENS_DB`` nao foi usada.")
$lines.Add("- ``password_hash`` nao sera migrado.")
$lines.Add("- ``eh_admin`` nao sera migrado.")
$lines.Add("- ``must_change`` nao sera migrado.")
$lines.Add("- ``source = legacy_ens_db`` sera aplicado apenas no Apply futuro.")
$lines.Add("- ``source_metadata`` sera preenchido apenas no Apply futuro.")
$lines.Add("- Campos vazios nao sobrescrevem campos existentes pela politica do importador.")
$lines.Add("- Status existente no PostgreSQL sera preservado pela politica do importador.")
$discardedText = $sensitiveDiscarded -join ", "
$lines.Add("- Campos sensiveis descartados no DryRun: ``$discardedText``.")
$lines.Add("")

$lines.Add("## Achados e riscos")
$lines.Add("")
foreach ($warning in @($enriched.warnings)) {
    $lines.Add("- Warning: $warning")
}
foreach ($errorItem in @($enriched.errors)) {
    $lines.Add("- Erro de enriquecimento: $errorItem")
}
if ($decision -eq "BLOCKED_FOR_APPLY") {
    $lines.Add("- Bloqueio: ha usuario previsto para atualizacao com papel/identidade sensivel ou risco operacional que exige revisao humana antes do Apply.")
} elseif ($decision -eq "APPROVED_WITH_WARNINGS") {
    $lines.Add("- Ressalva: ha conta sensivel ignorada pela politica e/ou duplicidades por matricula/login, mas sem risco tecnico bloqueante detectado.")
} else {
    $lines.Add("- Nenhum bloqueio ou ressalva operacional detectado.")
}
$lines.Add("")

$lines.Add("## Decisao pre-Apply")
$lines.Add("")
$lines.Add("**$decision**")
$lines.Add("")
if ($decision -eq "BLOCKED_FOR_APPLY") {
    $lines.Add("Antes do Apply, validar explicitamente o usuario previsto para atualizacao e confirmar que os campos listados podem receber metadados de origem legada.")
} else {
    $lines.Add("Apply pode ser considerado somente apos revisao humana, novo backup UAT e autorizacao explicita. A conta sensivel marcada como skipped nao sera atualizada automaticamente.")
}
$lines.Add("")

$lines.Add("## Proximo passo recomendado")
$lines.Add("")
if ($decision -eq "BLOCKED_FOR_APPLY") {
    $lines.Add("1. Revisar o usuario previsto para atualizacao.")
    $lines.Add("2. Confirmar se a conta sensivel pode receber ``source`` e ``source_metadata`` do legado.")
    $lines.Add("3. Reexecutar esta revisao pre-Apply.")
} else {
    $lines.Add("1. Fazer novo backup UAT:")
    $lines.Add("")
    $lines.Add('```powershell')
    $lines.Add(".\scripts\ops\backup-db.ps1 -ProjectName itam_uat")
    $lines.Add('```')
    $lines.Add("")
    $lines.Add("2. Executar Apply somente com autorizacao explicita:")
    $lines.Add("")
    $lines.Add('```powershell')
    $lines.Add('python scripts/import_legacy_ens_db_to_postgres.py `')
    $lines.Add('  --sqlite-path "C:\Users\estevao.quality\Desktop\Desktop\Assinatura\static\data\ens.db" `')
    $lines.Add('  --mode Apply `')
    $lines.Add('  --skip-sensitive-existing-users `')
    $lines.Add('  --sensitive-email "<EMAIL_SENSIVEL_VALIDADO_LOCALMENTE>" `')
    $lines.Add('  --confirm-apply APPLY_LEGACY_ENS_DB')
    $lines.Add('```')
}
$lines.Add("")

$outputFullPath = if ([System.IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath
} else {
    Join-Path $ProjectRoot $OutputPath
}
$outputDir = Split-Path -Parent $outputFullPath
if (-not (Test-Path -LiteralPath $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}
$lines | Set-Content -LiteralPath $outputFullPath -Encoding UTF8

Write-Host "Pre-Apply review generated: $OutputPath"
Write-Host "Decision: $decision"
Write-Host "Apply executed: no"
