#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

def analyze_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as f: rows = list(csv.DictReader(f))
    cols = rows[0].keys() if rows else []
    missing = sum(1 for row in rows for v in row.values() if v in ('', None))
    dupes = len(rows) - len({tuple(row.items()) for row in rows})
    return {'rows': len(rows), 'columns': len(list(cols)), 'missing_values': missing, 'duplicate_rows': max(dupes, 0)}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('input', nargs='?'); ap.add_argument('--report'); ap.add_argument('--dry-run', action='store_true', default=True); a = ap.parse_args()
    data = {'tool': 'spreadsheet_offline_analyzer', 'dry_run': a.dry_run, 'status': 'dry_run'}
    if a.input:
        p = Path(a.input)
        if p.suffix.lower() == '.csv' and p.exists(): data.update(analyze_csv(p))
        else: data['note'] = 'offline-only: no csv input analyzed'
    if a.report: Path(a.report).write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(json.dumps(data, indent=2))
if __name__ == '__main__': main()
