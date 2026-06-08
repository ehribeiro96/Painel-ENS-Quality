#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
SAMPLE = [{'ticket_id': 'SD-1001', 'category': 'incident', 'priority': 'high', 'status': 'closed'}, {'ticket_id': 'SD-1002', 'category': 'request', 'priority': 'medium', 'status': 'open'}]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--output', default='spreadsheet_sample.csv'); ap.add_argument('--report'); ap.add_argument('--dry-run', action='store_true', default=True); a = ap.parse_args()
    result = {'tool': 'spreadsheet_export_sample', 'output': a.output, 'dry_run': a.dry_run, 'status': 'dry_run'}
    if not a.dry_run:
        out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
        with out.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(SAMPLE[0].keys())); w.writeheader(); w.writerows(SAMPLE)
        result['status'] = 'written'
    if a.report: Path(a.report).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
if __name__ == '__main__': main()
