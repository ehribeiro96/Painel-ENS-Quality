#Requires -Version 5
param(
    [Parameter(Mandatory = $true)][string]$ResultsCsv,
    [Parameter(Mandatory = $true)][string]$KnownIssuesCsv,
    [Parameter(Mandatory = $true)][string]$SessionDir,
    [string]$OutputPath = "docs/UAT_EXECUTION_REPORT.md"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ResolvedSessionDir = Resolve-Path $SessionDir
$ResolvedResults = Resolve-Path $ResultsCsv
$ResolvedIssues = Resolve-Path $KnownIssuesCsv
$Output = Join-Path $Root $OutputPath

function Count-Where {
    param([object[]]$Items, [scriptblock]$Predicate)
    @($Items | Where-Object $Predicate).Count
}

$results = @(Import-Csv $ResolvedResults)
$issues = @(Import-Csv $ResolvedIssues)
$openIssues = @($issues | Where-Object { $_.issue_id -and $_.title -and $_.severity -and $_.status -notin @("Fixed", "Won't Fix", "Closed") })

$scenarioTotal = @($results | Where-Object { $_.scenario_id }).Count
$approved = Count-Where $results { $_.decision -eq "Aprovado" -or $_.status -eq "passed" }
$approvedWithCaveat = Count-Where $results { $_.decision -eq "Aprovado com ressalva" -or $_.status -eq "passed_with_caveat" }
$failed = Count-Where $results { $_.decision -eq "Reprovado" -or $_.status -eq "failed" }
$decidedScenarios = $approved + $approvedWithCaveat + $failed
$uatIncomplete = $scenarioTotal -lt 22 -or $decidedScenarios -eq 0

$severityOrder = @("BLOCKER", "CRITICAL", "HIGH", "MEDIUM", "LOW")
$severityCounts = [ordered]@{}
foreach ($severity in $severityOrder) {
    $severityCounts[$severity] = Count-Where $openIssues { $_.severity -eq $severity }
}

$areaCounts = $openIssues | Group-Object area | Sort-Object Name
$criticalScenarioFailures = @($results | Where-Object {
    $_.scenario_id -in @("UAT-001", "UAT-007", "UAT-011", "UAT-018", "UAT-019") -and
    ($_.decision -eq "Reprovado" -or $_.status -eq "failed")
})

$decision = "GO"
if ($severityCounts["BLOCKER"] -gt 0 -or $severityCounts["CRITICAL"] -gt 0 -or $criticalScenarioFailures.Count -gt 0) {
    $decision = "NO-GO"
} elseif ($uatIncomplete) {
    $decision = "GO COM RESSALVAS"
} elseif ($severityCounts["HIGH"] -gt 0 -or $severityCounts["MEDIUM"] -gt 0 -or $approvedWithCaveat -gt 0) {
    $decision = "GO COM RESSALVAS"
}

$manifestPath = Join-Path $ResolvedSessionDir "session_manifest.json"
$summaryPath = Join-Path $ResolvedSessionDir "final_summary.json"
$manifest = if (Test-Path $manifestPath) { Get-Content $manifestPath -Raw | ConvertFrom-Json } else { $null }
$summary = if (Test-Path $summaryPath) { Get-Content $summaryPath -Raw | ConvertFrom-Json } else { $null }

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Relatório de Execução UAT")
$lines.Add("")
$lines.Add("Gerado em: $((Get-Date).ToUniversalTime().ToString('o'))")
$lines.Add("")
$lines.Add("## Resumo Executivo")
$lines.Add("")
$lines.Add("Decisão recomendada: **$decision**")
$lines.Add("")
$lines.Add("## Ambiente Testado")
$lines.Add("")
$lines.Add(('- SessionDir: `{0}`' -f $ResolvedSessionDir))
if ($manifest) {
    $lines.Add(('- Project name: `{0}`' -f $manifest.project_name))
    $lines.Add(('- URL: `{0}`' -f $manifest.url))
    $lines.Add(('- Admin email: `{0}`' -f $manifest.admin_email))
    $lines.Add(('- Backup inicial: `{0}`' -f $manifest.initial_backup_manifest))
}
if ($summary) {
    $lines.Add(('- Backup final: `{0}`' -f $summary.final_backup_manifest))
    $lines.Add(('- Regressão pós-UAT: `{0}`' -f $summary.regression_result))
}
$lines.Add("")
$lines.Add("## Participantes")
$lines.Add("")
$participants = @($results | Where-Object { $_.executor } | Select-Object -ExpandProperty executor -Unique)
if ($participants.Count -eq 0) { $lines.Add("- Não informado no CSV.") } else { foreach ($p in $participants) { $lines.Add("- $p") } }
$lines.Add("")
$lines.Add("## Cenários")
$lines.Add("")
$lines.Add("- Total: $scenarioTotal")
$lines.Add("- Aprovados: $approved")
$lines.Add("- Aprovados com ressalva: $approvedWithCaveat")
$lines.Add("- Reprovados: $failed")
if ($uatIncomplete) {
    $lines.Add("- Observação: UAT incompleto ou CSV ainda sem decisões preenchidas.")
}
$lines.Add("")
$lines.Add("## Bugs Por Severidade")
$lines.Add("")
foreach ($severity in $severityOrder) {
    $lines.Add("- ${severity}: $($severityCounts[$severity])")
}
$lines.Add("")
$lines.Add("## Bugs Por Área")
$lines.Add("")
if (@($areaCounts).Count -eq 0) {
    $lines.Add("- Nenhum bug aberto informado.")
} else {
    foreach ($group in $areaCounts) {
        $area = if ($group.Name) { $group.Name } else { "Sem área" }
        $lines.Add("- ${area}: $($group.Count)")
    }
}
$lines.Add("")
foreach ($severity in $severityOrder) {
    $items = @($openIssues | Where-Object { $_.severity -eq $severity })
    $lines.Add("## ${severity}s")
    $lines.Add("")
    if ($items.Count -eq 0) {
        $lines.Add("- Nenhum.")
    } else {
        foreach ($issue in $items) {
            $lines.Add(('- `{0}` - {1} - cenário `{2}`' -f $issue.issue_id, $issue.title, $issue.scenario_id))
        }
    }
    $lines.Add("")
}
$lines.Add("## Evidências")
$lines.Add("")
$evidenceItems = @($results | Where-Object { $_.evidence_path })
if ($evidenceItems.Count -eq 0) {
    $lines.Add("- Evidências não informadas no CSV.")
} else {
    foreach ($item in $evidenceItems) {
        $lines.Add(('- `{0}`: `{1}`' -f $item.scenario_id, $item.evidence_path))
    }
}
$lines.Add("")
$lines.Add("## Resultado Pós-UAT")
$lines.Add("")
if ($summary) {
    foreach ($smoke in $summary.smoke_result) {
        $lines.Add(('- `{0}`: {1}' -f $smoke.path, $smoke.status))
    }
} else {
    $lines.Add("- `final_summary.json` não encontrado.")
}
$lines.Add("")
$lines.Add("## Decisão Recomendada")
$lines.Add("")
$lines.Add("**$decision**")
$lines.Add("")
$lines.Add("Critério aplicado: NO-GO para BLOCKER/CRITICAL abertos ou falha em fluxo crítico; GO COM RESSALVAS para HIGH/MEDIUM documentados; GO quando não há BLOCKER/CRITICAL/HIGH abertos e fluxos críticos aprovados.")

$lines | Set-Content -Path $Output -Encoding UTF8
Write-Host "UAT execution report generated: $Output"
