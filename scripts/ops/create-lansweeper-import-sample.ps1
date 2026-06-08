#Requires -Version 5
param(
    [Parameter(Mandatory = $true)]
    [string]$InputFile,

    [string]$OutputDir = "uat_evidence/import_samples",

    [int[]]$SampleSizes = @(50, 200)
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$InputPath = Resolve-Path -LiteralPath $InputFile
$OutputPath = Join-Path $Root $OutputDir
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "py"
}

if ([IO.Path]::GetExtension($InputPath).ToLowerInvariant() -ne ".xlsx") {
    throw "InputFile must be a .xlsx file exported from Lansweeper."
}

New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null

$sizesJson = $SampleSizes | ConvertTo-Json -Compress

$script = @'
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook, load_workbook

input_file = Path(sys.argv[1])
output_dir = Path(sys.argv[2])
sample_sizes = json.loads(sys.argv[3])

critical_columns = ["Name", "Type", "Custom1", "Serialnumber", "State", "Scanserver"]

if not input_file.exists():
    raise SystemExit(f"Input file not found: {input_file}")

workbook = load_workbook(input_file, read_only=True, data_only=False)
if "report" not in workbook.sheetnames:
    raise SystemExit("Required sheet 'report' was not found in the workbook.")

sheet = workbook["report"]
header_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), None)
if not header_row:
    raise SystemExit("Sheet 'report' does not contain a header row.")

headers = ["" if value is None else str(value).strip() for value in header_row]
missing = [column for column in critical_columns if column not in headers]
if missing:
    raise SystemExit("Missing critical Lansweeper columns: " + ", ".join(missing))

data_rows = list(sheet.iter_rows(min_row=2, values_only=True))
total_rows = len(data_rows)

safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", input_file.stem).strip("_") or "lansweeper_assets"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir.mkdir(parents=True, exist_ok=True)

created = []
for size in sample_sizes:
    if size <= 0:
        raise SystemExit(f"Invalid sample size: {size}")
    sample_workbook = Workbook()
    sample_sheet = sample_workbook.active
    sample_sheet.title = "report"
    sample_sheet.append(headers)
    for row in data_rows[:size]:
        sample_sheet.append(list(row))
    output_file = output_dir / f"{safe_stem}_sample_{size}_{timestamp}.xlsx"
    sample_workbook.save(output_file)
    created.append(
        {
            "sample_size": size,
            "rows_written": min(size, total_rows),
            "output_file": str(output_file),
        }
    )

manifest = {
    "created_at": datetime.now(timezone.utc).isoformat(),
    "source_file": str(input_file),
    "sheet": "report",
    "total_source_rows": total_rows,
    "column_count": len(headers),
    "critical_columns": critical_columns,
    "created_samples": created,
}
manifest_file = output_dir / f"{safe_stem}_samples_{timestamp}.manifest.json"
manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({**manifest, "manifest_file": str(manifest_file)}, ensure_ascii=False, indent=2))
'@

$tempScript = Join-Path $env:TEMP ("create_lansweeper_sample_{0}.py" -f ([guid]::NewGuid().ToString("N")))
try {
    Set-Content -Path $tempScript -Value $script -Encoding UTF8
    & $Python $tempScript $InputPath $OutputPath $sizesJson
    if ($LASTEXITCODE -ne 0) {
        throw "Sample generation failed."
    }
} finally {
    Remove-Item -LiteralPath $tempScript -Force -ErrorAction SilentlyContinue
}
