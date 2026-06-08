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
    ap = argparse.ArgumentParser(); ap.add_argument('--path', default='.'); ap.add_argument('--dry-run', action='store_true', default=False); args = ap.parse_args(); root = safe_path(args.path).resolve(); risks = []
    for p in root.rglob('*.ps1'):
        txt = p.read_text(encoding='utf-8', errors='ignore').lower()
        for needle in ['remove-item -recurse','restart-computer','set-executionpolicy','invoke-command','credential','password','token']:
            if needle in txt: risks.append({'file': str(p.relative_to(root)), 'needle': needle})
    print(json.dumps({'tool':'powershell_static_checker','root':str(root),'dry_run':args.dry_run,'risks':risks}, indent=2))


if __name__ == '__main__':
    main()
