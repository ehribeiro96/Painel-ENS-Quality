#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('schema', nargs='?')
    ap.add_argument('--schema', dest='schema_flag')
    ap.add_argument('--report')
    ap.add_argument('--dry-run', action='store_true', default=True)
    a = ap.parse_args()
    schema = a.schema_flag or a.schema or ''
    result = {'tool': 'spreadsheet_schema_validator', 'schema': schema, 'dry_run': a.dry_run, 'status': 'dry_run'}
    if a.report:
        Path(a.report).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    main()
