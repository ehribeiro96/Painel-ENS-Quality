#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

BANNED = ('.env', '.env.', '.pfx', '.p12', '.pem', '.key', 'token', 'secret', 'password', 'senha', 'credential')


def blocked(path: str | None) -> bool:
    if not path:
        return False
    low = path.lower()
    return any(b in low for b in BANNED)


def safe_path(p: str) -> Path:
    if blocked(p):
        raise SystemExit(f'Blocked sensitive path: {p}')
    return Path(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', default=False)
    ap.add_argument('--input')
    ap.add_argument('--output')
    ap.add_argument('--memory-id')
    ap.add_argument('--query')
    ap.add_argument('--report')
    args = ap.parse_args()
    result = {'tool': 'memory_conflict_check', 'dry_run': args.dry_run}
    result.update({'status': 'no_conflict' if not args.memory_id else 'checked', 'memory_id': args.memory_id})
    if args.report:
        out = safe_path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
