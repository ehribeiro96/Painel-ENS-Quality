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
    result = {'tool': 'office_format_router', 'dry_run': args.dry_run}
    if args.file_type == 'csv':
        route = 'parser_lige' if not args.requires_formatting else 'native_format_required'
    elif args.file_type == 'xlsx':
        route = 'openpyxl_or_m365_hml' if args.requires_formatting or args.requires_formulas or args.requires_tables else 'openpyxl'
    elif args.file_type == 'docx':
        route = 'python-docx_or_openxml'
    elif args.file_type == 'pptx':
        route = 'python-pptx_or_openxml'
    else:
        route = 'adobe_pdf_policy'
    result.update({'route': route, 'm365_hml_only': bool(args.requires_session or args.operation), 'reason': 'native fidelity policy'})
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
