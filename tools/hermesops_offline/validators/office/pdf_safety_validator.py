#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('input', nargs='?'); ap.add_argument('--sensitivity', default='low'); ap.add_argument('--signed', action='store_true'); ap.add_argument('--has-certificate', action='store_true'); ap.add_argument('--report'); ap.add_argument('--dry-run', action='store_true', default=True); a = ap.parse_args()
    blocked = a.signed or a.has_certificate or a.sensitivity.lower() in {'secret', 'restricted'}
    result = {'tool': 'pdf_safety_validator', 'input': a.input, 'sensitivity': a.sensitivity, 'signed': a.signed, 'has_certificate': a.has_certificate, 'dry_run': a.dry_run, 'blocked': blocked, 'status': 'blocked' if blocked else 'ok'}
    if a.report:
        Path(a.report).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    main()
