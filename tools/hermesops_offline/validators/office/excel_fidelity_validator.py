#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

BANNED = ('.env', '.env.', '.pfx', '.p12', '.pem', '.key', 'token', 'secret', 'password', 'senha', 'credential')


def blocked(value: str | None) -> bool:
    if not value:
        return False
    low = value.lower()
    return any(item in low for item in BANNED)


def guard_path(value: str | None) -> Path | None:
    if value is None:
        return None
    if blocked(value):
        raise SystemExit(f'Blocked sensitive path: {value}')
    return Path(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', default=False)
    ap.add_argument('--file-type', choices=['csv', 'xlsx', 'docx', 'pptx', 'pdf'])
    ap.add_argument('--requires-formatting', action='store_true', default=False)
    ap.add_argument('--requires-formulas', action='store_true', default=False)
    ap.add_argument('--requires-layout', action='store_true', default=False)
    ap.add_argument('--requires-tables', action='store_true', default=False)
    ap.add_argument('--requires-validation', action='store_true', default=False)
    ap.add_argument('--requires-session', action='store_true', default=False)
    ap.add_argument('--operation')
    ap.add_argument('--target-file')
    ap.add_argument('--table')
    ap.add_argument('--range')
    ap.add_argument('--output')
    args = ap.parse_args()
    result = {'tool': 'excel_fidelity_validator', 'dry_run': args.dry_run}
    result.update({'status': 'analyzed', 'requires_formatting': args.requires_formatting, 'requires_formulas': args.requires_formulas, 'requires_layout': args.requires_layout, 'requires_tables': args.requires_tables, 'requires_validation': args.requires_validation, 'fidelity_risk': 'high' if args.file_type == 'csv' and any([args.requires_formatting, args.requires_formulas, args.requires_layout, args.requires_tables, args.requires_validation]) else 'low'})
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
