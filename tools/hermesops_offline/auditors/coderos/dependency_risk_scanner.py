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
    ap = argparse.ArgumentParser(); ap.add_argument('--path', default='.'); ap.add_argument('--dry-run', action='store_true', default=False); args = ap.parse_args(); root = safe_path(args.path).resolve(); deps = []
    for name in ['requirements.txt','package.json','pyproject.toml','poetry.lock','pnpm-lock.yaml','package-lock.json']:
        for p in root.rglob(name): deps.append(str(p.relative_to(root)))
    print(json.dumps({'tool':'dependency_risk_scanner','root':str(root),'dry_run':args.dry_run,'dependency_files':deps[:100],'status':'review_required' if deps else 'no_dependencies'}, indent=2))


if __name__ == '__main__':
    main()
