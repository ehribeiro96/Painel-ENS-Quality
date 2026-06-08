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
    ap = argparse.ArgumentParser()
    ap.add_argument('--path', default='.')
    ap.add_argument('--dry-run', action='store_true', default=False)
    args = ap.parse_args()
    root = safe_path(args.path).resolve()
    found = set()
    text = ''
    for p in list(root.rglob('*'))[:4000]:
        if p.is_file() and p.stat().st_size < 200000:
            try:
                text += p.read_text(encoding='utf-8', errors='ignore').lower() + '\n'
            except Exception:
                pass
    markers = {
        'python': ['pyproject.toml', 'requirements.txt', 'setup.py'],
        'fastapi': ['fastapi'],
        'node': ['package.json'],
        'react': ['react'],
        'vite': ['vite'],
        'nextjs': ['next'],
        'powershell': ['.ps1'],
        'docker': ['compose.yaml', 'dockerfile'],
        'qdrant': ['qdrant'],
        'office': ['enterprise_office_skills', 'tools/office'],
        'm365': ['graph', 'office scripts'],
        'modding': ['modding'],
    }
    for stack, needles in markers.items():
        if any(n in text for n in needles):
            found.add(stack)
    print(json.dumps({'tool': 'stack_detector', 'path': str(root), 'dry_run': args.dry_run, 'stacks': sorted(found)}, indent=2))

if __name__ == '__main__':
    main()
