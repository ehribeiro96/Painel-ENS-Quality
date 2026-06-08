#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
BLOCKED = ('.git', '.env', 'node_modules', 'venv', 'build', 'dist', '.venv', '__pycache__')
SENSITIVE = ('.env', '.pfx', '.p12', '.pem', '.key', 'token', 'secret', 'password', 'senha', 'credential')

def is_blocked(path: str) -> bool:
    low = path.lower()
    return any(x in low for x in SENSITIVE)

def safe_path(path: str) -> Path:
    if is_blocked(path):
        raise SystemExit(f'Blocked sensitive path: {path}')
    return Path(path)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--path', default='.'); ap.add_argument('--dry-run', action='store_true', default=False); args = ap.parse_args(); root = safe_path(args.path).resolve(); hits = []; forbidden = ['crack','keygen','bypass','anti-cheat','malware','evasion','license']
    for p in root.rglob('*'):
        if p.is_file() and p.stat().st_size < 200000:
            txt = p.read_text(encoding='utf-8', errors='ignore').lower()
            for f in forbidden:
                if f in txt: hits.append({'file': str(p.relative_to(root)), 'term': f})
    print(json.dumps({'tool':'modding_project_analyzer','root':str(root),'dry_run':args.dry_run,'forbidden_hits':hits[:100]}, indent=2))


if __name__ == '__main__':
    main()
