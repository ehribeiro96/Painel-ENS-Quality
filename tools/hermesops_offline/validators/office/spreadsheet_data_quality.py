#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('input', nargs='?'); ap.add_argument('--report'); ap.add_argument('--dry-run', action='store_true', default=True); a = ap.parse_args()
    findings = []
    if a.input and Path(a.input).suffix.lower() == '.csv' and Path(a.input).exists():
        with Path(a.input).open(newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        if rows:
            cols = list(rows[0].keys())
            for idx, row in enumerate(rows, start=1):
                empty = [k for k, v in row.items() if not v]
                if empty:
                    findings.append(f'row {idx} missing values in: {", ".join(empty)}')
            if len(rows) != len({tuple(r.items()) for r in rows}):
                findings.append('duplicate rows detected')
            findings.append('columns detected: ' + ', '.join(cols))
        else:
            findings.append('empty csv')
    else:
        findings.append('offline-only: no csv input analyzed')
    result = {'tool': 'spreadsheet_data_quality', 'dry_run': a.dry_run, 'findings': findings, 'status': 'ok'}
    if a.report:
        Path(a.report).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    main()
