#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('input', nargs='?'); ap.add_argument('--allow-real-pptx', action='store_true'); ap.add_argument('--report'); ap.add_argument('--dry-run', action='store_true', default=True); a = ap.parse_args()
    result = {'tool': 'pptx_structure_reader', 'input': a.input, 'dry_run': a.dry_run, 'blocked': not a.allow_real_pptx, 'slides': [], 'status': 'offline'}
    if a.report:
        Path(a.report).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    main()
