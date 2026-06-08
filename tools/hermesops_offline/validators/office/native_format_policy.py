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
    result = {'tool': 'native_format_policy', 'dry_run': args.dry_run}
    fidelity = any([args.requires_formatting, args.requires_formulas, args.requires_layout, args.requires_tables, args.requires_validation])
    csv_allowed = args.file_type == 'csv' and not fidelity
    native_required = args.file_type in {'xlsx', 'docx', 'pptx', 'pdf'} or fidelity
    if args.file_type == 'csv' and fidelity:
        reason = 'CSV does not preserve fidelity-sensitive Office features'
        risk = 'high'
    elif args.file_type == 'csv':
        reason = 'CSV acceptable for simple interchange'
        risk = 'low'
    else:
        reason = 'Native format preferred for Office fidelity'
        risk = 'medium'
    result.update({'csv_allowed': csv_allowed, 'native_format_required': native_required, 'reason': reason, 'risk_level': risk})
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
