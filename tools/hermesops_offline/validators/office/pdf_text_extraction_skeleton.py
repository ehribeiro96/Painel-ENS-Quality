#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('input', nargs='?'); ap.add_argument('--sensitivity', default='low'); ap.add_argument('--report'); ap.add_argument('--dry-run', action='store_true', default=True); a = ap.parse_args()
    blocked = a.sensitivity.lower() in {'secret', 'restricted'}
    result = {'tool': 'pdf_text_extraction_skeleton', 'input': a.input, 'sensitivity': a.sensitivity, 'dry_run': a.dry_run, 'blocked': blocked, 'status': 'blocked' if blocked else 'dry_run'}
    if a.report:
        Path(a.report).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    main()
