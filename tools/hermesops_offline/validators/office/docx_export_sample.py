#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--output', default='docx_sample.md'); ap.add_argument('--report'); ap.add_argument('--dry-run', action='store_true', default=True); a = ap.parse_args()
    Path(a.output).write_text('# Synthetic DOCX sample stub' + chr(10), encoding='utf-8')
    result = {'tool': 'docx_export_sample', 'output': a.output, 'dry_run': a.dry_run, 'status': 'written_md_stub'}
    if a.report:
        Path(a.report).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    main()
