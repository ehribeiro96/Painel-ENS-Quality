#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ALLOWED = {'spreadsheet', 'docx', 'pptx', 'pdf', 'text'}
BLOCK_WORDS = ('secret', 'restricted', '.env', 'token', 'credential', 'password', 'senha', '.pfx', '.p12', '.pem', '.key')


def blocked_value(value: str | None) -> bool:
    if not value:
        return False
    low = value.lower()
    return any(word in low for word in BLOCK_WORDS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('job_type', nargs='?')
    ap.add_argument('--job-type', dest='job_type_flag')
    ap.add_argument('--target')
    ap.add_argument('--sensitivity', default='sanitized')
    ap.add_argument('--report')
    ap.add_argument('--dry-run', action='store_true', default=True)
    a = ap.parse_args()

    job_type = a.job_type_flag or a.job_type or ''
    target = a.target or ''
    blocked = blocked_value(job_type) or blocked_value(target) or a.sensitivity.lower() in {'secret', 'restricted'}
    ok = (job_type in ALLOWED) and not blocked
    result = {
        'tool': 'office_job_router',
        'job_type': job_type,
        'target': target,
        'sensitivity': a.sensitivity,
        'dry_run': a.dry_run,
        'allowed_types': sorted(ALLOWED),
        'blocked_words': list(BLOCK_WORDS),
        'status': 'routed' if ok else 'blocked',
        'blocked': not ok,
    }
    if a.report:
        Path(a.report).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
